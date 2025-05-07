"""
Tool for editing files in the project.
"""

import os
import difflib
from typing import Dict, List, Any

from ..models.file_info import FileInfo


class FileEditor:
    def __init__(self, target_dir: str):
        self.target_dir = target_dir

    def edit_file(
        self, file_path: str, edit_instructions: str, project_index: Dict[str, FileInfo]
    ):
        """Edit a file based on instructions"""
        # Normalize path
        if not file_path.startswith(self.target_dir):
            full_path = os.path.join(self.target_dir, file_path)
        else:
            full_path = file_path

        rel_path = os.path.relpath(full_path, self.target_dir)

        if not os.path.exists(full_path):
            print(f"❌ File not found: {file_path}")
            return

        print(f"✏️ Editing {file_path} based on: '{edit_instructions}'")

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Here we would integrate with an LLM to generate the edits
            # For now, we'll just show the file and prompt for manual edits
            print("\nCurrent file content:")
            print("---------------------")
            lines = content.split("\n")
            for i, line in enumerate(lines):
                print(f"{i+1:4d} | {line}")
            print("---------------------")

            print("\nWhat changes would you like to make?")
            print("1. Replace a line")
            print("2. Add new lines")
            print("3. Delete lines")
            print("4. Cancel")

            choice = input("> ")

            if choice == "1":
                line_num = int(input("Line number to replace: "))
                new_line = input("New content: ")
                if 1 <= line_num <= len(lines):
                    old_content = content
                    lines[line_num - 1] = new_line
                    new_content = "\n".join(lines)
                    self._save_file(full_path, new_content)
                    self._show_diff(old_content, new_content)
                    self._update_index(rel_path, new_content, project_index)
                else:
                    print("❌ Invalid line number")

            elif choice == "2":
                line_num = int(input("After which line? "))
                new_lines = []
                print("Enter new lines (empty line to finish):")
                while True:
                    new_line = input()
                    if not new_line:
                        break
                    new_lines.append(new_line)

                if 0 <= line_num <= len(lines):
                    old_content = content
                    lines = lines[:line_num] + new_lines + lines[line_num:]
                    new_content = "\n".join(lines)
                    self._save_file(full_path, new_content)
                    self._show_diff(old_content, new_content)
                    self._update_index(rel_path, new_content, project_index)
                else:
                    print("❌ Invalid line number")

            elif choice == "3":
                start = int(input("Start line: "))
                end = int(input("End line: "))
                if 1 <= start <= end <= len(lines):
                    old_content = content
                    lines = lines[: start - 1] + lines[end:]
                    new_content = "\n".join(lines)
                    self._save_file(full_path, new_content)
                    self._show_diff(old_content, new_content)
                    self._update_index(rel_path, new_content, project_index)
                else:
                    print("❌ Invalid line range")

            elif choice == "4":
                print("Edit cancelled")

            else:
                print("❌ Invalid choice")

        except Exception as e:
            print(f"❌ Error editing file: {str(e)}")

    def _save_file(self, file_path: str, content: str):
        """Save content to a file"""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ File saved: {file_path}")
        except Exception as e:
            print(f"❌ Error saving file: {str(e)}")

    def _update_index(
        self, rel_path: str, content: str, project_index: Dict[str, FileInfo]
    ):
        """Update the project index with the new file content"""
        if rel_path in project_index:
            file_info = project_index[rel_path]
            file_info.content = content

            # Clear existing structure
            file_info.functions = []
            file_info.classes = []
            file_info.imports = []

            # Re-extract structure for Python files
            if file_info.language == "python":
                from ..tools.indexer import ProjectIndexer

                indexer = ProjectIndexer(self.target_dir)
                indexer.extract_python_structure(file_info)

    def _show_diff(self, old_content: str, new_content: str):
        """Show a diff of the changes"""
        old_lines = old_content.splitlines()
        new_lines = new_content.splitlines()
        diff = difflib.unified_diff(
            old_lines, new_lines, lineterm="", fromfile="before", tofile="after"
        )

        print("\nChanges made:")
        for line in diff:
            if line.startswith("+") and not line.startswith("+++"):
                print(f"\033[92m{line}\033[0m")  # Green for additions
            elif line.startswith("-") and not line.startswith("---"):
                print(f"\033[91m{line}\033[0m")  # Red for deletions
            else:
                print(line)
