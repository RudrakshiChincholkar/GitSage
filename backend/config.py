import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_PAT = os.getenv("GITHUB_PAT")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GITHUB_PAT:
    raise Exception("GITHUB_PAT not found in environment")

if not GROQ_API_KEY:
    raise Exception("GROQ_API_KEY not found in environment")