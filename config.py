import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.0-flash"

if not GEMINI_API_KEY or GEMINI_API_KEY == "your_api_key_here":
    raise ValueError("GEMINI_API_KEY not set. Please add your API key to .env file.")
