from embeddings.embedding_router import EmbeddingRouter
from vectorstore.chroma_store import ChromaStore  # Note: moved to vectorstore


class EmbeddingPipeline:
    """
    High-level embedding pipeline that routes chunks to the appropriate
    embedder(s) and persists them into ChromaDB.
    """

    def __init__(self):
        self.router = EmbeddingRouter()
        self.store = ChromaStore()

    def run(self, chunks, repo_url: str, repo_version: str | None = None):
        """
        Embed and store a batch of chunks for a given repository.

        Args:
            chunks: Iterable of chunk dicts from the ingestion pipeline.
            repo_url: Original repository URL (may be normalized internally).
            repo_version: Optional repository version / signature derived from
                          GitHub metadata (e.g. `pushed_at`). When provided,
                          it is stored so we can skip re-embedding unchanged
                          repositories on subsequent ingestions.
        """
        print(f"Embedding {len(chunks)} chunks...")

        embedded_chunks = self.router.route_and_embed(chunks)

        print("Storing in ChromaDB...")
        self.store.add_embeddings(embedded_chunks, repo_url)

        if repo_version:
            # Mark this repo/version as fully ingested so future runs can
            # cheaply determine if work can be skipped.
            self.store.mark_repo_ingested(repo_url, repo_version)

        print("Embedding pipeline completed.")