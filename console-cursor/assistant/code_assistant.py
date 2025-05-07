"""
Core CodeAssistant class that manages the interaction with the user and coordinates tools.
"""

import os
import traceback
from typing import List, Dict, Any, Optional

from .tools.indexer import ProjectIndexer
from .tools.analyzer import ProjectAnalyzer
from .tools.executor import CommandExecutor
from .tools.bug_finder import BugFinder
from .tools.file_editor import FileEditor
from .models.file_info import FileInfo


class CodeAssistant:
    def __init__(self, target_dir: str):
        self.target_dir = os.path.abspath(target_dir)
        self.project_index = {}
        self.project_summary = ""
        self.history = []

        # Initialize tools
        self.indexer = ProjectIndexer(self.target_dir)
        self.analyzer = ProjectAnalyzer(self.target_dir)
        self.executor = CommandExecutor(self.target_dir)
        self.bug_finder = BugFinder(self.target_dir)
        self.file_editor = FileEditor(self.target_dir)

    def run(self):
        """Main loop for the code assistant"""
        print(f"🤖 Code Assistant initialized for: {self.target_dir}")
        print("Analyzing project structure...")

        # Initial project analysis
        self.project_index = self.indexer.index_project()
        self.project_summary = self.analyzer.analyze_project(self.project_index)

        while True:
            try:
                user_input = input(
                    "\n🧑‍💻 What would you like me to help with? (type 'exit' to quit): "
                )

                if user_input.lower() in ["exit", "quit"]:
                    print("Goodbye! 👋")
                    break

                self.process_request(user_input)

            except KeyboardInterrupt:
                print("\nGoodbye! 👋")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                print(traceback.format_exc())

    def process_request(self, request: str):
        """Process the user request and call appropriate tools"""
        self.history.append({"role": "user", "content": request})

        # Simple command parsing
        if request.startswith("find "):
            query = request[5:]
            self.indexer.find_in_codebase(self.project_index, query)
        elif request.startswith("fix "):
            file_path = request[4:]
            self.bug_finder.analyze_and_fix_bugs(file_path)
        elif request.startswith("run "):
            command = request[4:]
            self.executor.execute_code(command)
        elif request.startswith("edit "):
            parts = request[5:].split(" ", 1)
            if len(parts) == 2:
                file_path, edit_instructions = parts
                self.file_editor.edit_file(
                    file_path, edit_instructions, self.project_index
                )
            else:
                print("❌ Usage: edit <file_path> <instructions>")
        elif request.startswith("analyze "):
            file_path = request[8:]
            self.analyzer.analyze_file(file_path, self.project_index)
        elif request.lower() == "help":
            self.show_help()
        else:
            # General request - try to understand and take appropriate action
            if (
                "bug" in request.lower()
                or "error" in request.lower()
                or "fix" in request.lower()
            ):
                print("I'll help you identify and fix bugs in your code.")
                self.bug_finder.analyze_project_for_bugs(self.project_index)
            elif "create" in request.lower() or "new file" in request.lower():
                self.handle_file_creation(request)
            elif "structure" in request.lower() or "overview" in request.lower():
                self.analyzer.show_project_structure(self.project_index)
            else:
                print("I'll try to help with your request.")
                # Here we would integrate with an LLM for more complex requests
                print("For specific actions, try commands like:")
                self.show_help()

    def show_help(self):
        """Display available commands"""
        print("\n📚 Available commands:")
        print("  find <query>              - Search for code or files in the project")
        print("  fix <file_path>           - Analyze and fix bugs in a file")
        print(
            "  run <command>             - Execute a command in the project directory"
        )
        print("  edit <file_path> <instr>  - Edit a file based on instructions")
        print("  analyze <file_path>       - Analyze a specific file")
        print("  help                      - Show this help message")
        print("  exit                      - Exit the assistant")
        print("\nYou can also ask general questions about the codebase.")

    def handle_file_creation(self, request: str):
        """Handle requests to create new files"""
        print("To create a new file, please specify:")
        file_path = input("File path (relative to project): ")

        if not file_path:
            print("❌ File path cannot be empty")
            return

        full_path = os.path.join(self.target_dir, file_path)

        # Check if file already exists
        if os.path.exists(full_path):
            print(f"⚠️ File already exists: {file_path}")
            overwrite = input("Overwrite? (yes/no): ")
            if overwrite.lower() not in ["yes", "y"]:
                print("File creation cancelled")
                return

        # Create directories if needed
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        print("Enter file content (type 'EOF' on a new line when done):")
        lines = []
        while True:
            line = input()
            if line == "EOF":
                break
            lines.append(line)

        content = "\n".join(lines)

        # Save the file
        try:
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ File created: {file_path}")

            # Update the index
            _, ext = os.path.splitext(file_path)
            language = self.indexer.get_language_from_extension(ext)

            file_info = FileInfo(path=file_path, content=content, language=language)

            # Extract code structure for Python files
            if language == "python":
                self.indexer.extract_python_structure(file_info)

            self.project_index[file_path] = file_info

        except Exception as e:
            print(f"❌ Error creating file: {str(e)}")
