import requests
from io import BytesIO
import json
import docx
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain_core.output_parsers import JsonOutputParser
from PyPDF2 import PdfReader

# Load environment variables
load_dotenv()


# === STEP 1: Download Resume from Public URL ===
def fetch_resume_text_from_url(url):
    response = requests.get(url)
    content_type = response.headers.get("Content-Type", "").lower()

    if "pdf" in content_type:
        reader = PdfReader(BytesIO(response.content))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    elif "word" in content_type or url.endswith(".docx"):
        doc = docx.Document(BytesIO(response.content))
        text = "\n".join(para.text for para in doc.paragraphs)
    elif "text" in content_type or url.endswith(".txt"):
        text = response.text
    else:
        raise ValueError("Unsupported file type. Only PDF, DOCX, or TXT are supported.")

    return text.strip()


# SYSTEM PROMPT
system_prompt = """
You are an intelligent resume parser and formatter trained to process CVs and extract clean, structured data for display in a standardized UI. You must return only valid JSON.

Your job is to:
1. Analyze the resume and extract relevant information.
2. Clean up, normalize, and remove any irrelevant or repeated data.
3. Output the information in the following structured JSON format, even if some fields are empty.

The JSON schema must follow this format:

{{
  "basic_info": {{
    "full_name": "",
    "job_title": "",
    "location": "",
    "phone": "",
    "email": "",
    "website": "",
    "years_of_experience": ""
  }},
  "professional_summary": "",
  "skills": [],
  "semantic_skills": [],
  "certifications": [],
  "education": [
    {{
      "degree": "",
      "institution": "",
      "start_year": "",
      "end_year": "",
      "location": ""
    }}
  ],
  "work_experience": [
    {{
      "job_title": "",
      "company": "",
      "start_date": "",
      "end_date": "",
      "location": "",
      "description": ""
    }}
  ],
  "projects": [
    {{
      "title": "",
      "description": "",
      "technologies": []
    }}
  ],
  "awards": [],
  "languages": [],
  "interests": [],
  "career_insights": {{
    "resume_score": "",
    "predicted_experience_level": "",
    "branding_score": "",
    "executive_summary": "",
    "keywords_matched": [],
    "job_fit_scores": [
      {{
        "role": "",
        "match_percentage": ""
      }}
    ]
  }}
}}

General Rules:
- Normalize all dates to YYYY-MM format or just YYYY if month is unknown.
- Keep bullet points inside the `description` fields as `\n`-separated text.
- If some fields are missing in the resume, leave them empty or as empty arrays.
- `career_insights` fields may be machine-generated; use placeholders unless available.
"""

# === STEP 3: LangChain Setup ===
prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(system_prompt),
        HumanMessagePromptTemplate.from_template("{resume_text}"),
    ]
)

parser = JsonOutputParser()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
chain = prompt | llm | parser


# === STEP 4: Process from URL ===
def process_resume_from_url(public_url):
    resume_text = fetch_resume_text_from_url(public_url)
    structured_json = chain.invoke({"resume_text": resume_text})
    return structured_json


# === Example Usage ===
if __name__ == "__main__":
    resume_url = "https://enigma-demo.webledger.in/GauravSharma_CV.pdf"
    result = process_resume_from_url(resume_url)

    print(json.dumps(result, indent=2))
