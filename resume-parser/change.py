import os
from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Step 1: Set your OpenAI API key
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# Step 2: Define source and destination folders
SOURCE_FOLDER = "/Users/divamtech/Downloads/brahmansamajrajasthan.com"
DESTINATION_FOLDER = "/Users/divamtech/Downloads/brahmansamajrajasthan.com_php"

# Step 3: Files to consider
VALID_EXTENSIONS = [".aspx", ".master", ".master.cs"]


# Step 4: Read file content
def read_file(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


# Step 5: Call OpenAI to convert
def convert_to_php(file_name, file_content):
    system_prompt = (
        "You are a skilled software engineer specializing in converting ASP.NET WebForms projects to modern PHP.\n"
        "You will be given an ASP.NET file (.aspx, or .master) and you must carefully understand its structure, "
        "logic, event handlers, and UI elements.\n"
        "Generate equivalent, properly structured, clean PHP code.\n"
        "Use best practices in PHP, and make sure that server-side C# logic is correctly transformed into PHP backend logic.\n"
        "Preserve comments and make the output understandable.\n"
        "Maintain the functionality, but adjust for PHP conventions (like echo instead of Response.Write).\n"
        "Convert Master Pages appropriately to PHP layouts.\n"
        "Generate complete, ready-to-save PHP code.\n"
        "Do not include any other text or comments in the output.\n"
        "Do not include further instructions in the output.\n"
    )

    user_prompt = f"File Name: {file_name}\n\nContent:\n{file_content}\n\nPlease convert this into PHP equivalent."

    response = client.chat.completions.create(
        model="gemini-2.0-flash",
        n=1,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    php_code = response.choices[0].message.content
    return php_code


# Step 6: Save converted PHP file
def save_php_file(original_path, php_code):
    relative_path = os.path.relpath(original_path, SOURCE_FOLDER)
    new_file_path = os.path.join(
        DESTINATION_FOLDER, Path(relative_path).with_suffix(".php")
    )

    os.makedirs(os.path.dirname(new_file_path), exist_ok=True)
    with open(new_file_path, "w", encoding="utf-8") as f:
        f.write(php_code)


# Step 7: Main conversion process
def convert_project():
    for root, dirs, files in os.walk(SOURCE_FOLDER):
        for file in files:
            if any(file.endswith(ext) for ext in VALID_EXTENSIONS):
                file_path = os.path.join(root, file)
                print(f"Processing: {file_path}")

                try:
                    content = read_file(file_path)
                    php_code = convert_to_php(file, content)
                    save_php_file(file_path, php_code)
                    print(f"Converted and saved: {file}")
                except Exception as e:
                    print(f"Failed to process {file_path}: {e}")


if __name__ == "__main__":
    convert_project()
