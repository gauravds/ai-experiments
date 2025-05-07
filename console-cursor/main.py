#!/usr/bin/env python3
"""
Code Assistant - A console-based programming assistant that helps analyze, modify, and fix code.
"""
import os
import sys
import argparse
from assistant.code_assistant import CodeAssistant


def main():
    """Main entry point for the Code Assistant application"""
    parser = argparse.ArgumentParser(
        description="Code Assistant - Help with programming tasks"
    )
    parser.add_argument(
        "target_dir",
        nargs="?",
        default=".",
        help="Target directory to analyze (default: current directory)",
    )
    parser.add_argument("--version", action="version", version="Code Assistant v0.1.0")

    args = parser.parse_args()

    # Normalize and validate the target directory
    target_dir = os.path.abspath(args.target_dir)
    if not os.path.isdir(target_dir):
        print(f"Error: {target_dir} is not a valid directory")
        sys.exit(1)

    # Initialize and run the assistant
    assistant = CodeAssistant(target_dir)
    assistant.run()


if __name__ == "__main__":
    main()
