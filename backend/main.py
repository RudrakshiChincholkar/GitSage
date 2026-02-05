import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from embeddings.embedder_manager import initialize_embedders
from repo_ingestion.unified_pipeline import ingest_repository, get_retriever
from qa.qa_engine import answer_question
from docs.doc_generator import generate_documentation


logger = logging.getLogger("gitsage.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Pre-loads embedding models on startup to avoid first-request latency.
    """
    print(" Starting GitSage API...")
    print("Pre-loading embedding models...")
    initialize_embedders()
    print(" Models loaded and ready!")
    yield
    print("Shutting down GitSage API...")


# Create app with lifespan
app = FastAPI(lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
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
async def ingest(request: IngestRequest):  # ← Added 'async'
    try:
        result = await ingest_repository(request.repo_url)  # ← Added 'await'
        return result
    except Exception as e:
        logger.exception("Error in /ingest endpoint")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
async def ask(request: QuestionRequest):
    try:
        answer = answer_question(request.repo_url, request.question)
        logger.info("[/ask] answer length: %s", len(answer))
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-docs")
async def generate_docs(request: DocumentationRequest):
    try:
        retriever = get_retriever()
        documentation = generate_documentation(request.repo_url, retriever)
        return {
            "status": "success",
            "sections": documentation
        }
    except Exception as e:
        logger.exception("Error in /generate-docs endpoint")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/debug/chroma-count")
async def debug_chroma_count():
    """Debug endpoint to check ChromaDB status"""
    from vectorstore.chroma_store import ChromaStore
    
    store = ChromaStore()
    code_count = store.code_collection.count()
    text_count = store.text_collection.count()
    
    code_sample = store.code_collection.get(limit=2, include=["metadatas"])
    text_sample = store.text_collection.get(limit=2, include=["metadatas"])
    
    return {
        "code_count": code_count,
        "text_count": text_count,
        "code_sample_metadatas": code_sample.get("metadatas", []),
        "text_sample_metadatas": text_sample.get("metadatas", [])
    }