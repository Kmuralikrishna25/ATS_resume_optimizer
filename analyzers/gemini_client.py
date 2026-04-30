import google.generativeai as genai
from config import GEMINI_API_KEY, GEMINI_MODEL

class GeminiClient:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(GEMINI_MODEL)

    def generate(self, prompt, system_instruction=None):
        try:
            if system_instruction:
                response = self.model.generate_content(
                    system_instruction + "\n\n" + prompt
                )
            else:
                response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"

    def analyze_resume(self, resume_text, job_description=None):
        prompt = self._build_analysis_prompt(resume_text, job_description)
        return self.generate(prompt)

    def _build_analysis_prompt(self, resume_text, job_description=None):
        prompt = f"""Analyze the following resume and provide a comprehensive ATS evaluation.

RESUME TEXT:
{resume_text}
"""
        if job_description:
            prompt += f"\nTARGET JOB DESCRIPTION:\n{job_description}\n"

        prompt += """
IMPORTANT: Provide your response ONLY in valid JSON format. Do not include any text before or after the JSON. Do not wrap the JSON in markdown code blocks.

{{
    "ats_score": <score from 0-100>,
    "keyword_analysis": {{
        "present_keywords": ["keyword1", "keyword2"],
        "missing_keywords": ["keyword1", "keyword2"],
        "suggested_keywords": ["keyword1", "keyword2"]
    }},
    "format_suggestions": [
        "suggestion1",
        "suggestion2"
    ],
    "section_analysis": {{
        "contact_info": {{
            "score": <0-100>,
            "feedback": "feedback text"
        }},
        "summary": {{
            "score": <0-100>,
            "feedback": "feedback text"
        }},
        "experience": {{
            "score": <0-100>,
            "feedback": "feedback text"
        }},
        "education": {{
            "score": <0-100>,
            "feedback": "feedback text"
        }},
        "skills": {{
            "score": <0-100>,
            "feedback": "feedback text"
        }}
    }},
    "overall_feedback": "overall feedback text",
    "optimized_resume": "full optimized resume text here"
}}

Be specific, actionable, and constructive in your feedback."""

        return prompt
