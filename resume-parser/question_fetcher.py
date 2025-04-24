import json
import os
from dotenv import load_dotenv
from typing import List, Dict, Any
from openai import OpenAI
import time

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

SYSTEM_PROMPT = """
You are a highly accurate MCQ (Multiple Choice Questions) generator for quizzes.

Your task is to generate an array of MCQs based on the provided topic or subject.

Follow these instructions strictly:
1. Each question must be formatted in **markdown** to allow highlighting important terms (e.g., `**bold**`, `*italic*`, `code` syntax).
2. Each question must have **4 options** labeled `A`, `B`, `C`, and `D`.
3. Return ONLY a valid JSON array of MCQs only supports markdown code blocks. without any explanations, or additional text.
4. Each JSON object must have the following keys:
   - `"question"`: The question in markdown format.
   - `"options"`: An object with 4 keys: `"A"`, `"B"`, `"C"`, `"D"` — each with its option as a string in markdown format.
   - `"answer"`: One of the letters `A`, `B`, `C`, or `D` indicating the correct answer.
   - `"level"`: An integer from 1 to 10 representing difficulty. Use 1 for beginner-level, 10 for expert-level.
5. Ensure all answers are factually correct.
6. Your entire response must be a valid JSON array that can be parsed directly with json.loads().
7. Keep language clear, concise, and relevant to the topic.

Example of the expected response format (this is exactly how your entire response should look):
[
  {
    "question": "What is FS in **Node.js**?",
    "options": {
      "A": "`File System` module to read, write and append the file.",
      "B": "Functions to create *reusable* codes.",
      "C": "System library to interact with **OS**.",
      "D": "`Node.js` internal file management system."
    },
    "answer": "A",
    "level": 2
  },
  {
    "question": "What is the output of below code\n```js\nconsole.log('hello', 'world')\n```",
    "options": {
      "A": "prints on console as `hello, world`",
      "B": "prints on console as `hello world`",
      "C": "prints on console as `hello world`",
      "D": "throws error as `Uncaught SyntaxError: Unexpected number`"
    },
    "answer": "C",
    "level": 1
  },
  {
    "question": "What is the right choice to get print the following html in nodejs\n```html\n<ul>\n\t<li> item 1 </li>\n\t<li> item 2 </li>\n\t</ul>\n```",
    "options": {
      "A": "```js\nlist = [1,2].map(x => `<li> ${x} </li>`).join('')\nel = `<ul>${list}</ul>`\n```",
      "B": "```js\nlist = [1,2].map(x => `<li> ${x} </li>`).join('')\nel = `<ul>\n\t${list}</ul>`\n```",
      "C": "```js\nlist = [1,2].map(x => `<li> ${x} </li>`).join('')\nel = `<ul>\n\t${list}\n\t</ul>`\n```",
      "D": "```js\nlist = [1,2].map(x => `<li> ${x} </li>`).join('\n\t')\nel = `<ul>\n\t${list}\n\t</ul>`\n```"
    },
    "answer": "D",
    "level": 3
  }
]
"""


def generate_mcqs(
    topic: str,
    num_sets: int = 10,
    difficulty: int = 5,
    code_questions: bool = False,
    extra_notes: str = None,
) -> List[Dict[str, Any]]:
    # Base prompt
    user_prompt = f"Generate {num_sets} multiple choice questions about {topic} with difficulty level {difficulty} on a scale of 1-10."

    # Add code-related instruction if requested
    if code_questions:
        user_prompt += "\nInclude at least 30% code-related questions with code snippets in the questions and/or answer options."

    # Add any extra notes from the user
    if extra_notes:
        user_prompt += f"\nAdditional instructions: {extra_notes}"

    response = client.chat.completions.create(
        model="gemini-2.0-flash",
        n=1,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )

    # Get the response content
    response_content = response.choices[0].message.content

    # Print the response for debugging
    print(f"Response received, length: {len(response_content)}")

    # Extract and parse JSON from response
    try:
        # Try to parse the content directly
        mcq_json = json.loads(response_content)
        return mcq_json
    except json.JSONDecodeError:
        # If response is not valid JSON, try to extract JSON part
        import re

        # Look for JSON array pattern in the response
        json_match = re.search(r"\[\s*{.*}\s*\]", response_content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        # Try to extract JSON from markdown code blocks
        code_block_match = re.search(
            r"```(?:json)?\s*([\s\S]*?)\s*```", response_content, re.DOTALL
        )
        if code_block_match:
            try:
                return json.loads(code_block_match.group(1))
            except json.JSONDecodeError:
                pass

        # Return empty list if JSON extraction fails
        print("Failed to parse JSON response from Gemini")
        print(
            "Response content:",
            (
                response_content[:200] + "..."
                if len(response_content) > 200
                else response_content
            ),
        )
        return []


def save_mcqs_to_file(mcqs: List[Dict[str, Any]], filename: str = "mcqs.json"):
    """Save generated MCQs to a JSON file."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(mcqs, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(mcqs)} MCQs to {filename}")


if __name__ == "__main__":
    topic = input("Enter the topic for MCQs (e.g., Node.js): ")
    try:
        num_sets = int(input("Enter the number of MCQ sets to generate: "))
    except ValueError:
        print("Invalid number, using default of 10")
        num_sets = 10

    try:
        difficulty = int(input("Enter difficulty level (1-10, where 10 is hardest): "))
        if difficulty < 1 or difficulty > 10:
            print("Invalid difficulty level, using default of 5")
            difficulty = 5
    except ValueError:
        print("Invalid difficulty level, using default of 5")
        difficulty = 5

    code_questions = (
        input("Include code-related questions? (y/n): ").lower().startswith("y")
    )

    # Additional notes prompt
    extra_notes = input(
        "Any additional notes for the question generator? (press Enter to skip): "
    )

    mcqs = generate_mcqs(
        topic,
        num_sets,
        difficulty,
        code_questions=code_questions,
        extra_notes=extra_notes if extra_notes else None,
    )

    if mcqs:
        # Add timestamp to filename to ensure uniqueness
        timestamp = int(time.time() * 1000)  # Epoch time in milliseconds
        filename = f"{topic.replace(' ', '_').lower()}_mcqs_{timestamp}.json"
        save_mcqs_to_file(mcqs, filename)
    else:
        print("No MCQs were generated. Please try again.")
