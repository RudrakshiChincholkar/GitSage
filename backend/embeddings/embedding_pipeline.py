from embeddings.embedding_router import EmbeddingRouter
from vectorstore.chroma_store import ChromaStore  # Note: moved to vectorstore

class EmbeddingPipeline:
    def __init__(self):
        self.router = EmbeddingRouter()
        self.store = ChromaStore()
    def run(self, chunks, repo_url: str):  # ← ADD repo_url parameter
        print(f"Embedding {len(chunks)} chunks...")

        embedded_chunks = self.router.route_and_embed(chunks)

        print("Storing in ChromaDB...")
        self.store.add_embeddings(embedded_chunks, repo_url)  # ← PASS repo_url

        print("Embedding pipeline completed.")