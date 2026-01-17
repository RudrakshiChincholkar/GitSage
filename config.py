import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_PAT = os.getenv("GITHUB_PAT")

if not GITHUB_PAT:
    raise Exception("GITHUB_PAT not found in environment")
