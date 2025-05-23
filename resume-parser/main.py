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
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
import tempfile
import os

# Load environment variables
load_dotenv()


# === STEP 1: Download Resume from Public URL ===
def fetch_resume_text_from_url(url):
    response = requests.get(url)
    content_type = response.headers.get("Content-Type", "").lower()

    # Create a temporary file to save the downloaded content
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(response.content)
        temp_path = temp_file.name

    try:
        if "pdf" in content_type or url.endswith(".pdf"):
            loader = PyPDFLoader(temp_path)
            docs = loader.load()
            text = "\n".join(doc.page_content for doc in docs)
        elif "word" in content_type or url.endswith(".docx"):
            loader = Docx2txtLoader(temp_path)
            docs = loader.load()
            text = "\n".join(doc.page_content for doc in docs)
        elif "text" in content_type or url.endswith(".txt"):
            loader = TextLoader(temp_path)
            docs = loader.load()
            text = "\n".join(doc.page_content for doc in docs)
        else:
            raise ValueError(
                "Unsupported file type. Only PDF, DOCX, or TXT are supported."
            )

        return text.strip()
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)


# SYSTEM PROMPT
system_prompt = """
You are an advanced resume parser and career advisor.
Your goal is to convert raw resume text into a well-structured JSON output suitable for ATS systems.

Follow these rules strictly:

1. Maintain standard ATS-friendly formatting:
   - Use plain text only (no emojis, symbols, or formatting characters)
   - Avoid long paragraphs; use clear bullet points where applicable
   - Use proper field labels and separate responsibilities cleanly

2. Extract and structure the following fields:
   - name, email, phone, location
   - linkedin, github, website
   - summary
   - skills (technical and domain skills)
   - semantic_skills (inferred based on profile)
   - languages (spoken/written fluency)
   - education (degree, institution, location, years, GPA)
   - experience (role, company, location, start/end date, responsibilities)
   - projects (title, description, tech_stack, url)
   - certifications (e.g., RN License, CPR, with issuer and year)
   - awards (title, description, year)
   - publications (title, publisher, year, url)
   - patents (title, document_id, year)
   - interests (professional or personal interests)
   - current_job_title (most recent or primary)
   - classified_job_title (standardized/normalized role)
   - job_level (Internship, Entry-level, Mid-level, Senior, Leadership)
   - total_experience_years (rounded number)
   - resume_score (0-100)
   - strengths_vs_weaknesses (concise summary)
   - next_roles (predicted next job titles)
   - required_skills_to_advance (skills needed for next career step)
   - career_path_prediction (logical job trajectory from current role)
   - job_fit_scores (list of recommended jobs with match_percent and reasons)
   - promotion_projection (estimated_time and readiness_percent)
   - branding_tone (concise resume tone: e.g. 'Confident & Growth-Oriented')
   - executive_summary (1–2 line branded summary of candidate's value)

3. Enhance the parsed content:
   - Use active voice, concise phrasing
   - Normalize vague skill names (e.g., 'experienced with EHR' → 'Electronic Health Records (EHR)')
   - Break combined entries (e.g., 'Geriatric and Pediatric specialization') into two skills
   - Deduplicate and clean skills into standard terminology
   - Do not include language fluency in the  skills  array
   - Standardise  skills  array
   - skills array should include skills relevant to resume  skills  array
   - Instead, extract language fluency and place in the  languages  array
   - Example: 'Fluent in Spanish' → 'Spanish'
   - Structure experience into clean bullet points under  description 
   - Standardize formatting of dates, companies, job titles, and institutions
   - Infer semantic skills and total experience if not explicitly mentioned
   - Infer and populate  current_job_title  from the most recent experience if not explicitly mentioned
   - If resume contains licensing or credentials, populate under  certifications  with appropriate issuer/year
   - Populate  resume_score  (0–100) based on completeness, clarity, formatting, and ATS readiness
   - Provide a brief  strengths_vs_weaknesses  comparison (concise bullet or sentence summary)
   - Normalize skill entries for consistency, e.g., avoid phrases like "Experienced with..."

4. Identify and extract any *projects*, even if they are embedded inside work experience:
   - Treat any sentence that describes building, launching, or contributing to a tool, product, or system as a project
   - Extract such information into the  projects  array, even if not under a 'Projects' section
   - Each project must include:
     -  name : inferred or explicit project title
     -  description : brief summary of what the project accomplished
     -  tech_stack : list of tools or technologies used
     -  url : if explicitly mentioned, else null
   - Place all such extracted items in a dedicated  projects  array at the top level

5. Add career insights:
   - Predict  next_roles 
   - Recommend  required_skills_to_advance 
   - Estimate  resume_score  (0–100) based on quality of content
   - Summarize  strengths_vs_weaknesses 
   - Provide a 2-line  executive_summary  and overall  branding_tone 
   - Suggest  career_path_prediction 
   - Return  promotion_projection  with estimated_time and readiness_percent
   - Generate  job_fit_scores : each with job_title, match_percent, and reasons

6. Classify job title:
   - Extract the user's current role into  current_job_title 
   - Output a standardized  classified_job_title  (e.g., 'Registered Nurse')
   - Output  job_level  from ['Internship', 'Entry-level', 'Mid-level', 'Senior', 'Leadership']

7. If any field is not available, return it as null (for objects/strings/numbers) or an empty array (for lists).
   Do not leave any key out from the structured JSON response.

8. Very Important, Dont change the location in any of the field. You can enhance the location but cant change it to some other.

Return only the final structured JSON using the function format.

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
llm = ChatOpenAI(model="gpt-4o", temperature=0)
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
