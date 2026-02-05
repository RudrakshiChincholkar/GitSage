# retrieval/retriever.py
import numpy as np

def cosine_similarity(a, b):
    """Compute cosine similarity between two vectors."""
    a = np.array(a)
    b = np.array(b)
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def flatten_embedding(embedding):
    """
    If embedding is 2D (multiple vectors per document), take mean along axis 0.
    Otherwise, return as-is.
    """
    arr = np.array(embedding)
    if arr.ndim == 2:
        return arr.mean(axis=0)
    return arr

class Retriever:
    def __init__(self, store, code_embedder, text_embedder):
        """
        store: ChromaStore instance
        code_embedder: embedding model for code
        text_embedder: embedding model for text
        """
        self.store = store
        self.code_embedder = code_embedder
        self.text_embedder = text_embedder

    def retrieve(self, query, top_k=5, repo_url=None):
        # 1️⃣ Embed the query in both code and text embedding spaces
        code_query_vector = self.code_embedder.embed([query])[0]
        text_query_vector = self.text_embedder.embed([query])[0]

        # 2️⃣ Retrieve raw results from ChromaDB (both code and text)
        code_results_raw = self.store.query_code(
            code_query_vector,
            top_k * 3,
            repo_url=repo_url  # ← PASS repo_url
        )
        text_results_raw = self.store.query_text(
            text_query_vector,
            top_k * 3,
            repo_url=repo_url  # ← PASS repo_url
        )

        # Debug: show raw query results shapes
        try:
            code_count = len(code_results_raw.get("ids", []))
        except Exception:
            code_count = 0
        try:
            text_count = len(text_results_raw.get("ids", []))
        except Exception:
            text_count = 0

        print(f"[RETRIEVER_NEW] code_results_raw count: {code_count}, text_results_raw count: {text_count}, repo_url={repo_url}")

        # 3️⃣ Process code results (unwrap nested lists from Chroma)
        code_results = []
        if code_results_raw.get("ids") and len(code_results_raw["ids"]) > 0:
            for i in range(len(code_results_raw["ids"][0])):  # ← Access [0][i]
                doc_vector = flatten_embedding(code_results_raw["embeddings"][0][i])  # ← Access [0][i]
                sim = cosine_similarity(code_query_vector, doc_vector)

                # Safely unwrap metadata
                metadata_item = code_results_raw["metadatas"][0][i]  # ← Access [0][i]
                if isinstance(metadata_item, list):
                    metadata_item = metadata_item[0] if len(metadata_item) > 0 else {}

                code_results.append({
                    "similarity": sim,
                    "document": code_results_raw["documents"][0][i],  # ← Access [0][i]
                    "metadata": metadata_item,
                    "source": "code"
                })

        # 4️⃣ Process text results (unwrap nested lists from Chroma)
        text_results = []
        if text_results_raw.get("ids") and len(text_results_raw["ids"]) > 0:
            for i in range(len(text_results_raw["ids"][0])):  # ← Access [0][i]
                doc_vector = flatten_embedding(text_results_raw["embeddings"][0][i])  # ← Access [0][i]
                sim = cosine_similarity(text_query_vector, doc_vector)

                # Safely unwrap metadata
                metadata_item = text_results_raw["metadatas"][0][i]  # ← Access [0][i]
                if isinstance(metadata_item, list):
                    metadata_item = metadata_item[0] if len(metadata_item) > 0 else {}

                text_results.append({
                    "similarity": sim,
                    "document": text_results_raw["documents"][0][i],  # ← Access [0][i]
                    "metadata": metadata_item,
                    "source": "text"
                })

        # 5️⃣ Merge results and sort by similarity
        combined = code_results + text_results
        combined.sort(key=lambda x: x["similarity"], reverse=True)

        # 6️⃣ Return top_k
        return combined[:top_k]
