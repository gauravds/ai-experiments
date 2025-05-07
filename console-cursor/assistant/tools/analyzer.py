"""
Tool for analyzing project structure and individual files.
"""

import os
import ast
from typing import Dict, List, Any

from ..models.file_info import FileInfo


class ProjectAnalyzer:
    def __init__(self, target_dir: str):
        self.target_dir = target_dir

    def analyze_project(self, project_index: Dict[str, FileInfo]) -> str:
        """Analyze the project to understand its structure and purpose"""
        print("🔍 Analyzing project...")

        # Count files by language
        language_counts = {}
        for file_info in project_index.values():
            language_counts[file_info.language] = (
                language_counts.get(file_info.language, 0) + 1
            )

        # Look for key files that might indicate project type
        has_package_json = "package.json" in project_index
        has_requirements_txt = "requirements.txt" in project_index
        has_setup_py = "setup.py" in project_index
        has_gemfile = "Gemfile" in project_index
        has_cargo_toml = "Cargo.toml" in project_index

        # Generate project summary
        summary_parts = [f"Project in {self.target_dir}"]

        # Add language distribution
        if language_counts:
            lang_summary = ", ".join(
                [
                    f"{count} {lang} files"
                    for lang, count in sorted(
                        language_counts.items(), key=lambda x: x[1], reverse=True
                    )
                ]
            )
            summary_parts.append(f"Contains {lang_summary}")

        # Add project type guesses
        project_types = []
        if has_package_json:
            project_types.append("JavaScript/Node.js")
        if has_requirements_txt or has_setup_py:
            project_types.append("Python")
        if has_gemfile:
            project_types.append("Ruby")
        if has_cargo_toml:
            project_types.append("Rust")

        if project_types:
            summary_parts.append(f"Appears to be a {'/'.join(project_types)} project")

        project_summary = ". ".join(summary_parts)
        print(f"📊 {project_summary}")
        return project_summary

    def analyze_file(self, file_path: str, project_index: Dict[str, FileInfo]):
        """Analyze a specific file"""
        # Normalize path
        if not file_path.startswith(self.target_dir):
            full_path = os.path.join(self.target_dir, file_path)
        else:
            full_path = file_path

        rel_path = os.path.relpath(full_path, self.target_dir)

        if not os.path.exists(full_path):
            print(f"❌ File not found: {file_path}")
            return

        print(f"🔍 Analyzing {file_path}...")

        # Check if file is in index
        if rel_path in project_index:
            file_info = project_index[rel_path]

            print(f"\nFile: {rel_path}")
            print(f"Language: {file_info.language}")

            if file_info.imports:
                print("\nImports:")
                for imp in file_info.imports:
                    print(f"  {imp}")

            if file_info.functions:
                print("\nFunctions:")
                for func in file_info.functions:
                    args = ", ".join(func["args"])
                    print(f"  {func['name']}({args}) - line {func['line']}")
                    if func["docstring"]:
                        first_line = func["docstring"].split("\n")[0]
                        print(f"    {first_line}")

            if file_info.classes:
                print("\nClasses:")
                for cls in file_info.classes:
                    print(f"  {cls['name']} - line {cls['line']}")
                    if cls["docstring"]:
                        first_line = cls["docstring"].split("\n")[0]
                        print(f"    {first_line}")

                    if cls["methods"]:
                        print("    Methods:")
                        for method in cls["methods"]:
                            args = ", ".join(method["args"])
                            print(
                                f"      {method['name']}({args}) - line {method['line']}"
                            )
        else:
            # File not in index, analyze it now
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()

                _, ext = os.path.splitext(file_path)
                language = self._get_language_from_extension(ext)

                print(f"\nFile: {rel_path}")
                print(f"Language: {language}")
                print(f"Size: {len(content)} bytes")

                # Count lines of code
                lines = content.split("\n")
                print(f"Lines: {len(lines)}")

                # For Python files, try to extract more info
                if language == "python":
                    try:
                        tree = ast.parse(content)
                        functions = [
                            node
                            for node in ast.walk(tree)
                            if isinstance(node, ast.FunctionDef)
                        ]
                        classes = [
                            node
                            for node in ast.walk(tree)
                            if isinstance(node, ast.ClassDef)
                        ]

                        print(f"Functions: {len(functions)}")
                        print(f"Classes: {len(classes)}")
                    except SyntaxError:
                        print("⚠️ Could not parse Python file (syntax error)")

            except Exception as e:
                print(f"❌ Error analyzing file: {str(e)}")

    def show_project_structure(self, project_index: Dict[str, FileInfo]):
        """Display the project structure"""
        print("\n📁 Project Structure:")

        # Group files by directory
        directories = {}
        for file_path in project_index.keys():
            dir_name = os.path.dirname(file_path)
            if not dir_name:
                dir_name = "."

            if dir_name not in directories:
                directories[dir_name] = []

            directories[dir_name].append(os.path.basename(file_path))

        # Print directory structure
        for dir_name, files in sorted(directories.items()):
            if dir_name == ".":
                print("📂 (root)")
            else:
                print(f"📂 {dir_name}")

            for file in sorted(files):
                print(f"  📄 {file}")

    def _get_language_from_extension(self, ext: str) -> str:
        """Map file extension to programming language"""
        extension_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".html": "html",
            ".css": "css",
            ".java": "java",
            ".c": "c",
            ".cpp": "cpp",
            ".h": "c",
            ".hpp": "cpp",
            ".go": "go",
            ".rs": "rust",
            ".rb": "ruby",
            ".php": "php",
            ".sh": "bash",
            ".md": "markdown",
            ".json": "json",
            ".xml": "xml",
            ".yaml": "yaml",
            ".yml": "yaml",
        }
        return extension_map.get(ext.lower(), "")
