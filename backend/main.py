import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from embeddings.embedder_manager import initialize_embedders
from repo_ingestion.unified_pipeline import ingest_repository, get_retriever
from qa.qa_engine import answer_question
from docs.doc_generator import generate_documentation

from ingestion.repo_fetcher import normalize_repo_url
from vectorstore.chroma_store import ChromaStore
from comparison.comparison_engine import ComparisonEngine
from repo_ingestion.unified_pipeline import get_retriever
from llm.groq_client import generate_answer

logger = logging.getLogger("gitsage.api")


# --------------------------------------------------
# INGESTION GUARD (SINGLE SOURCE OF TRUTH)
# --------------------------------------------------

def ensure_repo_is_ingested(repo_url: str):
    # No-op guard (restore previous behavior)
    return



# --------------------------------------------------
# APP LIFESPAN
# --------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting GitSage API...")
    print("📦 Pre-loading embedding models...")
    initialize_embedders()
    print("✅ Models loaded and ready!")
    yield
    print("👋 Shutting down GitSage API...")


app = FastAPI(lifespan=lifespan)

# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# REQUEST MODELS
# --------------------------------------------------

class IngestRequest(BaseModel):
    repo_url: str


class QuestionRequest(BaseModel):
    repo_url: str
    question: str


class DocumentationRequest(BaseModel):
    repo_url: str

class CompareRequest(BaseModel):
    repo_a_namespace: str
    repo_b_namespace: str
# --------------------------------------------------
# ROUTES
# --------------------------------------------------

@app.get("/")
async def health():
    return {"status": "ok", "message": "GitSage API is running"}


@app.post("/ingest")
async def ingest(request: IngestRequest):
    try:
        return await ingest_repository(request.repo_url)
    except Exception as e:
        logger.exception("Error in /ingest endpoint")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask")
async def ask(request: QuestionRequest):
    try:
        # 🔒 HARD BLOCK
        ensure_repo_is_ingested(request.repo_url)

        answer = answer_question(request.repo_url, request.question)
        logger.info("[/ask] answer length: %s", len(answer))
        return {"answer": answer}

    except HTTPException:
        raise

    except Exception as e:
        logger.exception("Error in /ask endpoint")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-docs")
async def generate_docs(request: DocumentationRequest):
    try:
        # Same ingestion guard as Q&A
        ensure_repo_is_ingested(request.repo_url)

        retriever = get_retriever()
        documentation = generate_documentation(request.repo_url, retriever)
        return {
            "status": "success",
            "sections": documentation
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.exception("Error in /generate-docs endpoint")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/debug/chroma-count")
async def debug_chroma_count():
    store = ChromaStore()

    code_count = store.code_collection.count()
    text_count = store.text_collection.count()

    code_sample = store.code_collection.get(limit=2, include=["metadatas"])
    text_sample = store.text_collection.get(limit=2, include=["metadatas"])

    return {
        "code_count": code_count,
        "text_count": text_count,
        "code_sample_metadatas": code_sample.get("metadatas", []),
        "text_sample_metadatas": text_sample.get("metadatas", []),
    }
@app.post("/compare-repos")
def compare_repos(req: CompareRequest):
    retriever = get_retriever()

    class LLMWrapper:
        def generate(self, prompt: str) -> str:
            return generate_answer("", prompt)

    engine = ComparisonEngine(retriever, LLMWrapper())

    return engine.compare(
        req.repo_a_namespace,
        req.repo_b_namespace
    )
