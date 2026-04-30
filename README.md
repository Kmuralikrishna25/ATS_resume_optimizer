# ATS Resume Optimizer

An AI-powered resume optimization tool that analyzes your resume and provides actionable suggestions to improve your ATS (Applicant Tracking System) score.

## Features

- ATS Score (0-100)
- Keyword Analysis & Suggestions
- Format Suggestions
- Section-wise Analysis
- Ready-made Optimized Resume Download

## Setup

1. Install dependencies:
`ash
pip install -r requirements.txt
`

2. Set up your Gemini API key:
- Copy .env.example to .env
- Add your Google Gemini API key to .env

Get your API key: https://aistudio.google.com/app/apikey

## Usage

Run the Streamlit app:
`ash
streamlit run app.py
`

Upload your resume (PDF or DOCX) and optionally paste a job description for targeted optimization.

## Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **LLM**: Google Gemini API
- **File Parsing**: PyPDF2, pdfplumber, python-docx
