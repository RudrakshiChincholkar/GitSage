"""
Unified ingestion pipeline that uses the better ingestion approach
while maintaining compatibility with existing Q&A and Docs features.
"""

from repo_ingestion.step1_pipeline import run_step1
from repo_ingestion.file_processor import run_step2_validation
from embeddings.embedding_pipeline import EmbeddingPipeline
from vectorstore.chroma_store import ChromaStore


def ingest_repository(repo_url: str) -> dict:
    """
    Complete repository ingestion pipeline.
    
    Args:
        repo_url: GitHub repository URL
        
    Returns:
        dict: Status and chunk count
    """
    
    print(f"[1/3] Fetching and downloading repository files...")
    # Step 1: Fetch from GitHub API, filter, download
    downloaded_files = run_step1(repo_url)
    print(f"✓ Downloaded {len(downloaded_files)} files")
    
    print(f"[2/3] Cleaning, validating, and chunking...")
    # Step 2: Clean, validate, and chunk with language-specific logic
    chunks = run_step2_validation(downloaded_files)
    print(f"✓ Created {len(chunks)} chunks")
    
    print(f"[3/3] Embedding and storing in ChromaDB...")
    # Step 3: Route to appropriate embedders and store
    pipeline = EmbeddingPipeline()
    pipeline.run(chunks, repo_url)
    print(f"✓ Stored embeddings")
    
    return {
        "status": "success",
        "message": f"Successfully ingested {len(chunks)} chunks",
        "chunk_count": len(chunks)
    }


def get_retriever():
    """
    Initialize retriever for Q&A and documentation features.
    
    Returns:
        Retriever instance configured with dual embedders
    """
    from retrieval.retriever_new import Retriever
    from embeddings.code_embedder_new import CodeEmbedder
    from embeddings.sentence_embedder import SentenceEmbedder
    
    store = ChromaStore()
    code_embedder = CodeEmbedder()
    text_embedder = SentenceEmbedder()
    
    return Retriever(store, code_embedder, text_embedder)