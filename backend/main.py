from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ingestion.models import RepoRequest
from repo_ingestion.unified_pipeline import ingest_repository, get_retriever
from qa.qa_engine import answer_question
from docs.doc_generator import generate_documentation, format_documentation_markdown
from llm.groq_client import generate_answer
from ingestion.repo_summary import get_repo_summary

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

class DocumentationRequest(BaseModel):
    repo_url: str

# --------- Routes ---------

@app.get("/")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "message": "GitSage API is running"}

@app.post("/ingest")
async def ingest(request: IngestRequest):
    try:
        result = ingest_repository(request.repo_url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask")
async def ask(request: QuestionRequest):
    try:
        # Delegate to qa_engine.answer_question which builds a mode-aware prompt
        answer = answer_question(request.repo_url, request.question)

        # Log answer summary for debugging
        try:
            print(f"[API:/ask] answer length: {len(answer)}")
            print("[API:/ask] answer (first 300 chars):", answer[:300])
        except Exception:
            print("[API:/ask] answer generated (non-string or empty)")

        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-docs")
async def generate_docs(request: DocumentationRequest):
    try:
        # Use new retriever
        retriever = get_retriever()
        
        # Generate documentation (doc_generator already supports this)
        documentation = generate_documentation(request.repo_url, retriever)
        
        return {
            "status": "success",
            "sections": documentation
        }
    except Exception as e:
        import traceback
        print(f"\n❌ Error in /generate-docs endpoint:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/chroma-count")
async def debug_chroma_count():
    """Debug endpoint to check ChromaDB status"""
    from vectorstore.chroma_store import ChromaStore
    
    store = ChromaStore()
    code_count = store.code_collection.count()
    text_count = store.text_collection.count()
    
    # Get a sample to check repo_url metadata
    code_sample = store.code_collection.get(limit=2, include=["metadatas"])
    text_sample = store.text_collection.get(limit=2, include=["metadatas"])
    
    return {
        "code_count": code_count,
        "text_count": text_count,
        "code_sample_metadatas": code_sample.get("metadatas", []),
        "text_sample_metadatas": text_sample.get("metadatas", [])
    }