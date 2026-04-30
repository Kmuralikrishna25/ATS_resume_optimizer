from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import os
import json
import tempfile
import uuid
from dotenv import load_dotenv

load_dotenv()

from services.resume_parser import ResumeParser
from services.gemini_client import GeminiClient
from services.resume_generator import ResumeGenerator

app = FastAPI(title="ATS Resume Optimizer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

parser = ResumeParser()
gemini = GeminiClient()
generator = ResumeGenerator()


class JobDescriptionInput(BaseModel):
    job_description: Optional[str] = None


class AnalysisResult(BaseModel):
    ats_score: int
    keyword_analysis: dict
    format_suggestions: list
    section_analysis: dict
    overall_feedback: str
    optimized_resume: str


MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() == "true"


def get_mock_result(resume_text):
    return {
        "ats_score": 72,
        "keyword_analysis": {
            "present_keywords": ["Python", "React", "SQL", "Git", "Docker"],
            "missing_keywords": ["AWS", "CI/CD", "Kubernetes", "REST API"],
            "suggested_keywords": ["Agile", "Scrum", "TypeScript"]
        },
        "format_suggestions": [
            "Add quantifiable metrics to your experience section",
            "Include a summary at the top highlighting your key achievements",
            "Use consistent date formats throughout"
        ],
        "section_analysis": {
            "contact_info": {"score": 100, "feedback": "Complete and well-formatted contact information."},
            "summary": {"score": 60, "feedback": "Add a brief 2-3 line summary highlighting your top skills and achievements."},
            "experience": {"score": 70, "feedback": "Good experience listed. Add more metrics and results to strengthen it."},
            "education": {"score": 85, "feedback": "Education section is clear and complete."},
            "skills": {"score": 80, "feedback": "Strong skills section. Consider adding more technical skills relevant to your target role."}
        },
        "overall_feedback": "Your resume is solid but needs some keyword optimization and quantifiable achievements to score higher on ATS systems.",
        "optimized_resume": resume_text.upper().replace("\n", "\n") if resume_text else "OPTIMIZED RESUME CONTENT HERE"
    }


@app.post("/api/analyze")
async def analyze_resume(
    file: UploadFile = File(...),
    job_description: Optional[str] = Form(None)
):
    if not file.filename.lower().endswith(('.pdf', '.docx', '.doc')):
        raise HTTPException(status_code=400, detail="Unsupported file format")

    ext = os.path.splitext(file.filename)[1]
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
    tmp_file.write(await file.read())
    tmp_file.close()

    try:
        resume_text = parser.extract_text(tmp_file.name)
        if not resume_text:
            raise HTTPException(status_code=400, detail="Could not extract text from resume")

        if MOCK_MODE:
            return get_mock_result(resume_text)

        result = gemini.analyze_resume(resume_text, job_description)

        cleaned = result.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```", 2)[-2] if "```" in cleaned[3:] else cleaned
            if cleaned.startswith("json"):
                cleaned = cleaned[4:].strip()

        result_json = json.loads(cleaned)
        return result_json

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"Failed to parse AI response. Raw: {result[:200] if 'result' in dir() else 'N/A'}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.unlink(tmp_file.name)


@app.post("/api/download/{format}")
async def download_resume(
    format: str,
    content: str = Form(...)
):
    if format not in ["docx", "pdf", "txt"]:
        raise HTTPException(status_code=400, detail="Unsupported format")

    try:
        file_path = generator.generate(content, format)

        mime_map = {
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "pdf": "application/pdf",
            "txt": "text/plain"
        }

        response = FileResponse(
            file_path,
            media_type=mime_map[format],
            filename=f"optimized_resume.{format}"
        )
        response.headers["Content-Disposition"] = f"attachment; filename=optimized_resume.{format}"
        return response
    finally:
        if os.path.exists(file_path):
            os.unlink(file_path)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
