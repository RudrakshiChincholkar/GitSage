import numpy as np
from embeddings.embedder_manager import get_code_embedder, get_text_embedder


def cosine_similarity(a, b):
    """Compute cosine similarity between two vectors."""
    a = np.array(a)
    b = np.array(b)
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def flatten_embedding(embedding):
    """If embedding is 2D, take mean along axis 0."""
    arr = np.array(embedding)
    if arr.ndim == 2:
        return arr.mean(axis=0)
    return arr


class Retriever:
    def __init__(self, store, code_embedder=None, text_embedder=None):
        """
        store: ChromaStore instance
        code_embedder: Optional; uses singleton if not provided
        text_embedder: Optional; uses singleton if not provided
        """
        self.store = store
        # Use singletons if not explicitly provided
        self.code_embedder = code_embedder or get_code_embedder()
        self.text_embedder = text_embedder or get_text_embedder()

    def retrieve(self, query, top_k=5, repo_url=None):
        # Embed query once with each model
        code_query_vector = self.code_embedder.embed([query])[0]
        text_query_vector = self.text_embedder.embed([query])[0]

        # Query both collections
        code_results_raw = self.store.query_code(
            code_query_vector, top_k * 3, repo_url=repo_url
        )
        text_results_raw = self.store.query_text(
            text_query_vector, top_k * 3, repo_url=repo_url
        )

        # Process and merge results (same as before)
        code_results = []
        if code_results_raw.get("ids") and len(code_results_raw["ids"]) > 0:
            for i in range(len(code_results_raw["ids"][0])):
                doc_vector = flatten_embedding(code_results_raw["embeddings"][0][i])
                sim = cosine_similarity(code_query_vector, doc_vector)

                metadata_item = code_results_raw["metadatas"][0][i]
                if isinstance(metadata_item, list):
                    metadata_item = metadata_item[0] if len(metadata_item) > 0 else {}

                code_results.append({
                    "similarity": sim,
                    "document": code_results_raw["documents"][0][i],
                    "metadata": metadata_item,
                    "source": "code"
                })

        text_results = []
        if text_results_raw.get("ids") and len(text_results_raw["ids"]) > 0:
            for i in range(len(text_results_raw["ids"][0])):
                doc_vector = flatten_embedding(text_results_raw["embeddings"][0][i])
                sim = cosine_similarity(text_query_vector, doc_vector)

                metadata_item = text_results_raw["metadatas"][0][i]
                if isinstance(metadata_item, list):
                    metadata_item = metadata_item[0] if len(metadata_item) > 0 else {}

                text_results.append({
                    "similarity": sim,
                    "document": text_results_raw["documents"][0][i],
                    "metadata": metadata_item,
                    "source": "text"
                })

        combined = code_results + text_results
        combined.sort(key=lambda x: x["similarity"], reverse=True)
        return combined[:top_k]