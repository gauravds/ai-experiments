"""
Tool for indexing and searching the project files.
"""

import os
import re
import ast
from typing import Dict, List, Any

from ..models.file_info import FileInfo


class ProjectIndexer:
    def __init__(self, target_dir: str):
        self.target_dir = target_dir

    def index_project(self) -> Dict[str, FileInfo]:
        """Index all files in the project directory"""
        print("🔍 Indexing project files and structure...")

        # Get all files in the project directory
        all_files = []
        for root, _, files in os.walk(self.target_dir):
            for file in files:
                # Skip hidden files and directories
                if file.startswith(".") or "/.git/" in root:
                    continue

                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, self.target_dir)

                # Determine file language based on extension
                _, ext = os.path.splitext(file)
                language = self.get_language_from_extension(ext)

                if language:  # Only index files with recognized languages
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()

                        file_info = FileInfo(
                            path=rel_path, content=content, language=language
                        )

                        # Extract code structure for Python files
                        if language == "python":
                            self.extract_python_structure(file_info)

                        all_files.append(file_info)

                    except Exception as e:
                        print(f"⚠️ Error indexing {rel_path}: {str(e)}")

        # Store indexed files
        project_index = {file.path: file for file in all_files}
        print(f"✅ Indexed {len(project_index)} files")
        return project_index

    def extract_python_structure(self, file_info: FileInfo):
        """Extract functions, classes and imports from Python files"""
        try:
            tree = ast.parse(file_info.content)

            # Extract imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        file_info.imports.append(f"import {name.name}")
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for name in node.names:
                        file_info.imports.append(f"from {module} import {name.name}")

            # Extract functions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = {
                        "name": node.name,
                        "line": node.lineno,
                        "args": [arg.arg for arg in node.args.args],
                        "docstring": ast.get_docstring(node) or "",
                    }
                    file_info.functions.append(func_info)

                # Extract classes
                elif isinstance(node, ast.ClassDef):
                    class_methods = []
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            method_info = {
                                "name": item.name,
                                "line": item.lineno,
                                "args": [arg.arg for arg in item.args.args],
                                "docstring": ast.get_docstring(item) or "",
                            }
                            class_methods.append(method_info)

                    class_info = {
                        "name": node.name,
                        "line": node.lineno,
                        "methods": class_methods,
                        "docstring": ast.get_docstring(node) or "",
                    }
                    file_info.classes.append(class_info)

        except SyntaxError:
            # Handle syntax errors in Python files
            pass

    def get_language_from_extension(self, ext: str) -> str:
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

    def find_in_codebase(self, project_index: Dict[str, FileInfo], query: str):
        """Search for code or files in the project"""
        print(f"🔍 Searching for '{query}'...")

        results = []
        for file_path, file_info in project_index.items():
            if query.lower() in file_path.lower():
                results.append(f"File: {file_path}")

            # Search in file content
            if query.lower() in file_info.content.lower():
                lines = file_info.content.split("\n")
                for i, line in enumerate(lines):
                    if query.lower() in line.lower():
                        results.append(f"{file_path}:{i+1}: {line.strip()}")

        if results:
            print(f"Found {len(results)} matches:")
            for result in results[:10]:  # Limit to 10 results
                print(f"  {result}")

            if len(results) > 10:
                print(f"  ... and {len(results) - 10} more matches")
        else:
            print("No matches found")
