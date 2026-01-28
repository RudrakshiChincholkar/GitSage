from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ingestion.repo_fetcher import ingest_repo
from qa.qa_engine import answer_question

# SINGLE APP INSTANCE
app = FastAPI()

# CORS MUST BE ATTACHED TO THIS APP
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # dev mode
    allow_credentials=True,
    allow_methods=["*"],        # includes OPTIONS
    allow_headers=["*"],
)

# --------- Models ---------

class IngestRequest(BaseModel):
    repo_url: str

class QuestionRequest(BaseModel):
    repo_url: str
    question: str

# --------- Routes ---------

@app.post("/ingest")
async def ingest(request: IngestRequest):
    try:  # ADDED
        ingest_repo(request.repo_url)  # ADDED
        return {"status": "success"}  # ADDED
    except Exception as e:  # ADDED
        # Return a JSON error instead of crashing so the frontend can react.  # ADDED
        return {"status": "error", "message": str(e)}  # ADDED

@app.post("/ask")
async def ask(request: QuestionRequest):
    return answer_question(
        repo_url=request.repo_url,
        question=request.question
    )
