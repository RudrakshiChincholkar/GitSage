"""
Unified ingestion pipeline that uses the improved GitHub-based downloader
while maintaining compatibility with existing Q&A and Docs features.
"""

from repo_ingestion.step1_pipeline import run_step1
from repo_ingestion.file_processor import run_step2_validation
from embeddings.embedding_pipeline import EmbeddingPipeline
from vectorstore.chroma_store import ChromaStore
from ingestion.repo_fetcher import normalize_repo_url
from repo_ingestion.fetcher import get_repo_details, fetch_meta_repodata


def _get_repo_version(repo_url: str) -> str | None:
    """
    Derive a lightweight "version" string for a repository based on GitHub
    metadata. This is used to avoid re-embedding unchanged repositories.

    We intentionally avoid cloning/downloading the repo just to compute this.
    """
    details = get_repo_details(repo_url)
    if not details:
        return None

    owner, repo = details
    metadata = fetch_meta_repodata(owner, repo)

    # Prefer pushed_at (last content update); fall back to updated_at or a
    # combination of default_branch + node_id as a stable-ish identifier.
    return (
        metadata.get("pushed_at")
        or metadata.get("updated_at")
        or f"{metadata.get('default_branch', '')}:{metadata.get('node_id', '')}"
    )


def ingest_repository(repo_url: str) -> dict:
    """
    Complete repository ingestion pipeline.

    Steps:
    1) Use GitHub APIs to discover and download only relevant files.
    2) Clean, validate, and chunk the downloaded files.
    3) Embed chunks and store them in persistent ChromaDB collections.

    The pipeline is idempotent with respect to a (repo_url, repo_version)
    pair: if the same repo at the same version has already been ingested,
    ingestion is skipped to avoid redundant work.

    Args:
        repo_url: GitHub repository URL

    Returns:
        dict: Status and chunk count / skip information.
    """

    normalized_repo = normalize_repo_url(repo_url)
    repo_version = _get_repo_version(normalized_repo)

    store = ChromaStore()
    if store.is_repo_ingested(normalized_repo, repo_version):
        msg = f"Repository already ingested for version {repo_version}; skipping re-embedding."
        print(f"[INGEST] {msg}")
        return {
            "status": "success",
            "message": msg,
            "chunk_count": 0,
            "skipped": True,
        }

    print(f"[1/3] Fetching and downloading repository files...")
    # Step 1: Fetch from GitHub API, filter, download
    downloaded_files = run_step1(normalized_repo)
    print(f"✓ Downloaded {len(downloaded_files)} files")

    print(f"[2/3] Cleaning, validating, and chunking...")
    # Step 2: Clean, validate, and chunk with language-specific logic
    chunks = run_step2_validation(downloaded_files)
    print(f"✓ Created {len(chunks)} chunks")

    print(f"[3/3] Embedding and storing in ChromaDB...")
    # Step 3: Route to appropriate embedders and store
    pipeline = EmbeddingPipeline()
    pipeline.run(chunks, normalized_repo, repo_version=repo_version)
    print("✓ Stored embeddings")

    return {
        "status": "success",
        "message": f"Successfully ingested {len(chunks)} chunks",
        "chunk_count": len(chunks),
        "skipped": False,
    }


def get_retriever():
    """
    Initialize retriever for Q&A and documentation features.

    Returns:
        Retriever instance configured with dual embedders.
    """
    from retrieval.retriever_new import Retriever
    from embeddings.code_embedder_new import CodeEmbedder
    from embeddings.sentence_embedder import SentenceEmbedder

    store = ChromaStore()
    code_embedder = CodeEmbedder()
    text_embedder = SentenceEmbedder()

    return Retriever(store, code_embedder, text_embedder)