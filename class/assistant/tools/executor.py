"""
Tool for executing commands in the project directory.
"""

import subprocess


class CommandExecutor:
    def __init__(self, target_dir: str):
        self.target_dir = target_dir

    def execute_code(self, command: str):
        """Execute a command in the project directory"""
        print(f"🚀 Executing: {command}")

        try:
            # Run the command in the project directory
            process = subprocess.Popen(
                command,
                shell=True,
                cwd=self.target_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Stream output in real-time
            while True:
                output = process.stdout.readline()
                if output == "" and process.poll() is not None:
                    break
                if output:
                    print(output.strip())

            # Get return code
            return_code = process.poll()

            # Print any errors
            if return_code != 0:
                stderr = process.stderr.read()
                print(f"❌ Command failed with exit code {return_code}")
                print(stderr)
            else:
                print(f"✅ Command completed successfully")

        except Exception as e:
            print(f"❌ Error executing command: {str(e)}")
