"""
Tool for finding and fixing bugs in the codebase.
"""

import os
import ast
import json
import subprocess
import re
from typing import Dict, List, Any

from ..models.file_info import FileInfo


class BugFinder:
    def __init__(self, target_dir: str):
        self.target_dir = target_dir

    def analyze_and_fix_bugs(self, file_path: str):
        """Analyze a file for bugs and suggest fixes"""
        if not file_path:
            print("❌ Please specify a file to analyze")
            return

        # Normalize path
        if not file_path.startswith(self.target_dir):
            full_path = os.path.join(self.target_dir, file_path)
        else:
            full_path = file_path

        if not os.path.exists(full_path):
            print(f"❌ File not found: {file_path}")
            return

        print(f"🔍 Analyzing {file_path} for bugs...")

        # Get file extension to determine language
        _, ext = os.path.splitext(file_path)
        language = self._get_language_from_extension(ext)

        if language == "python":
            self.analyze_python_file(full_path)
        else:
            print(f"Bug analysis for {language} files is not yet implemented")

    def analyze_python_file(self, file_path: str):
        """Analyze a Python file for common issues"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Check for syntax errors
            try:
                ast.parse(content)
                print("✅ No syntax errors found")
            except SyntaxError as e:
                print(f"❌ Syntax error at line {e.lineno}, column {e.offset}: {e.msg}")
                self.suggest_syntax_fix(file_path, content, e)
                return

            # Run pylint for more detailed analysis
            try:
                result = subprocess.run(
                    ["pylint", "--output-format=json", file_path],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    print("✅ No issues found by pylint")
                else:
                    try:
                        issues = json.loads(result.stdout)
                        print(f"Found {len(issues)} potential issues:")
                        for issue in issues:
                            print(
                                f"  Line {issue['line']}: {issue['message']} ({issue['symbol']})"
                            )
                    except json.JSONDecodeError:
                        print("⚠️ Pylint output could not be parsed")

            except FileNotFoundError:
                print(
                    "⚠️ Pylint not found. Install with 'pip install pylint' for more detailed analysis"
                )

            # Check for common anti-patterns
            self.check_python_antipatterns(file_path, content)

        except Exception as e:
            print(f"❌ Error analyzing file: {str(e)}")

    def suggest_syntax_fix(self, file_path: str, content: str, error: SyntaxError):
        """Suggest a fix for a syntax error"""
        lines = content.split("\n")
        error_line = lines[error.lineno - 1] if error.lineno <= len(lines) else ""

        print(f"\nError line: {error_line}")

        # Common syntax errors and fixes
        if "EOL while scanning string literal" in error.msg:
            print("🔧 Suggestion: You might be missing a closing quote for a string")
            fixed_line = error_line + '"'  # Add closing quote
            print(f"Try: {fixed_line}")

        elif "unexpected EOF while parsing" in error.msg:
            print(
                "🔧 Suggestion: You might be missing a closing parenthesis, bracket, or brace"
            )

        elif "invalid syntax" in error.msg:
            if ":" in error_line and (
                "if" in error_line
                or "else" in error_line
                or "for" in error_line
                or "while" in error_line
            ):
                print(
                    "🔧 Suggestion: Check if you're missing a colon or have incorrect indentation"
                )
            else:
                print(
                    "🔧 Suggestion: Check for missing commas, operators, or incorrect syntax"
                )

        print("\nWould you like me to attempt to fix this error? (yes/no)")
        response = input("> ")
        if response.lower() in ["yes", "y"]:
            # Here we would implement more sophisticated auto-fixing
            print("Auto-fixing is not yet implemented")

    def check_python_antipatterns(self, file_path: str, content: str):
        """Check for common Python anti-patterns"""
        lines = content.split("\n")
        issues = []

        # Check for mutable default arguments
        mutable_defaults_pattern = r"def\s+\w+\s*\(.*=\s*(\[\]|{}|\(\))"
        for i, line in enumerate(lines):
            if re.search(mutable_defaults_pattern, line):
                issues.append(
                    f"Line {i+1}: Possible mutable default argument (can cause unexpected behavior)"
                )

        # Check for bare except clauses
        for i, line in enumerate(lines):
            if re.match(r"\s*except\s*:", line):
                issues.append(
                    f"Line {i+1}: Bare except clause (should specify exceptions to catch)"
                )

        # Check for == None instead of is None
        for i, line in enumerate(lines):
            if "== None" in line:
                issues.append(f"Line {i+1}: Using '== None' instead of 'is None'")

        if issues:
            print("\n⚠️ Potential code quality issues:")
            for issue in issues:
                print(f"  {issue}")
        else:
            print("✅ No common anti-patterns found")

    def analyze_project_for_bugs(self, project_index: Dict[str, FileInfo]):
        """Analyze the entire project for bugs"""
        print("🔍 Analyzing project for bugs...")

        # Count of files to analyze
        python_files = [
            path for path, info in project_index.items() if info.language == "python"
        ]

        if not python_files:
            print("No Python files found in the project")
            return

        print(f"Found {len(python_files)} Python files to analyze")

        # Check for pylint
        try:
            subprocess.run(["pylint", "--version"], capture_output=True, check=True)
            has_pylint = True
        except (subprocess.SubprocessError, FileNotFoundError):
            has_pylint = False
            print(
                "⚠️ Pylint not found. Install with 'pip install pylint' for better analysis"
            )

        issues_found = []

        # Analyze each Python file
        for file_path in python_files[:10]:  # Limit to 10 files for performance
            full_path = os.path.join(self.target_dir, file_path)
            print(f"\nAnalyzing {file_path}...")

            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Check for syntax errors
                try:
                    ast.parse(content)
                except SyntaxError as e:
                    issue = {
                        "file": file_path,
                        "line": e.lineno,
                        "message": f"Syntax error: {e.msg}",
                        "severity": "high",
                    }
                    issues_found.append(issue)
                    print(f"❌ Syntax error at line {e.lineno}: {e.msg}")
                    continue

                # Run pylint if available
                if has_pylint:
                    result = subprocess.run(
                        ["pylint", "--output-format=json", full_path],
                        capture_output=True,
                        text=True,
                    )

                    try:
                        pylint_issues = json.loads(result.stdout)
                        for issue in pylint_issues:
                            issues_found.append(
                                {
                                    "file": file_path,
                                    "line": issue["line"],
                                    "message": f"{issue['message']} ({issue['symbol']})",
                                    "severity": self._get_severity_from_pylint(
                                        issue["symbol"]
                                    ),
                                }
                            )
                    except json.JSONDecodeError:
                        pass

            except Exception as e:
                print(f"❌ Error analyzing {file_path}: {str(e)}")

        # Report findings
        if issues_found:
            print(f"\n🐛 Found {len(issues_found)} potential issues:")

            # Group by severity
            high_severity = [i for i in issues_found if i["severity"] == "high"]
            medium_severity = [i for i in issues_found if i["severity"] == "medium"]
            low_severity = [i for i in issues_found if i["severity"] == "low"]

            if high_severity:
                print(f"\n❌ {len(high_severity)} high severity issues:")
                for issue in high_severity:
                    print(f"  {issue['file']}:{issue['line']} - {issue['message']}")

            if medium_severity:
                print(f"\n⚠️ {len(medium_severity)} medium severity issues:")
                for issue in medium_severity[:5]:  # Show only top 5
                    print(f"  {issue['file']}:{issue['line']} - {issue['message']}")
                if len(medium_severity) > 5:
                    print(
                        f"  ... and {len(medium_severity) - 5} more medium severity issues"
                    )

            if low_severity:
                print(f"\n📝 {len(low_severity)} low severity issues")
                print("  Use 'analyze <file_path>' to see details for specific files")

            print("\nWould you like me to fix any of these issues? (yes/no)")
            response = input("> ")
            if response.lower() in ["yes", "y"]:
                # Here we would implement auto-fixing
                print("Auto-fixing is not yet implemented")
        else:
            print("✅ No issues found in the analyzed files")

    def _get_severity_from_pylint(self, symbol: str) -> str:
        """Map pylint symbols to severity levels"""
        high_severity = [
            "syntax-error",
            "undefined-variable",
            "undefined-name",
            "used-before-assignment",
            "not-callable",
            "no-member",
            "no-name-in-module",
            "import-error",
        ]
        medium_severity = [
            "unused-import",
            "unused-variable",
            "redefined-outer-name",
            "redefined-builtin",
            "unsubscriptable-object",
            "arguments-differ",
            "duplicate-code",
        ]

        if symbol in high_severity:
            return "high"
        elif symbol in medium_severity:
            return "medium"
        else:
            return "low"

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
