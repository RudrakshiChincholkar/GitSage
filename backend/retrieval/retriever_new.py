# retrieval/retriever_new.py
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
    """
    If embedding is 2D (multiple vectors per document), take mean along axis 0.
    Otherwise, return as-is.
    """
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
        """
        Retrieve relevant chunks for a query using dual embeddings.
        
        Args:
            query: Search query string
            top_k: Number of results to return
            repo_url: Optional repository URL filter
        
        Returns:
            List of dicts with 'similarity', 'document', 'metadata', 'source'
        """
        print(f"[RETRIEVER] Query: '{query[:50]}...', top_k={top_k}, repo_url={repo_url}")
        
        # 1️⃣ Embed the query in both code and text embedding spaces
        code_query_vector = self.code_embedder.embed([query])[0]
        text_query_vector = self.text_embedder.embed([query])[0]

        # 2️⃣ Retrieve raw results from ChromaDB (both code and text)
        code_results_raw = self.store.query_code(
            code_query_vector,
            top_k * 3,
            repo_url=repo_url
        )
        text_results_raw = self.store.query_text(
            text_query_vector,
            top_k * 3,
            repo_url=repo_url
        )

        # Debug: show raw query results
        try:
            code_count = len(code_results_raw.get("ids", [[]])[0]) if code_results_raw.get("ids") else 0
        except Exception:
            code_count = 0
        try:
            text_count = len(text_results_raw.get("ids", [[]])[0]) if text_results_raw.get("ids") else 0
        except Exception:
            text_count = 0

        print(f"[RETRIEVER] Retrieved: {code_count} code chunks, {text_count} text chunks")

        # 3️⃣ Process code results (unwrap nested lists from Chroma)
        code_results = []
        if code_results_raw.get("ids") and len(code_results_raw["ids"]) > 0 and len(code_results_raw["ids"][0]) > 0:
            for i in range(len(code_results_raw["ids"][0])):
                try:
                    doc_vector = flatten_embedding(code_results_raw["embeddings"][0][i])
                    sim = cosine_similarity(code_query_vector, doc_vector)

                    # Safely unwrap metadata
                    metadata_item = code_results_raw["metadatas"][0][i]
                    if isinstance(metadata_item, list):
                        metadata_item = metadata_item[0] if len(metadata_item) > 0 else {}

                    code_results.append({
                        "similarity": sim,
                        "document": code_results_raw["documents"][0][i],
                        "metadata": metadata_item,
                        "source": "code"
                    })
                except Exception as e:
                    print(f"[RETRIEVER] Error processing code result {i}: {e}")
                    continue

        # 4️⃣ Process text results (unwrap nested lists from Chroma)
        text_results = []
        if text_results_raw.get("ids") and len(text_results_raw["ids"]) > 0 and len(text_results_raw["ids"][0]) > 0:
            for i in range(len(text_results_raw["ids"][0])):
                try:
                    doc_vector = flatten_embedding(text_results_raw["embeddings"][0][i])
                    sim = cosine_similarity(text_query_vector, doc_vector)

                    # Safely unwrap metadata
                    metadata_item = text_results_raw["metadatas"][0][i]
                    if isinstance(metadata_item, list):
                        metadata_item = metadata_item[0] if len(metadata_item) > 0 else {}

                    text_results.append({
                        "similarity": sim,
                        "document": text_results_raw["documents"][0][i],
                        "metadata": metadata_item,
                        "source": "text"
                    })
                except Exception as e:
                    print(f"[RETRIEVER] Error processing text result {i}: {e}")
                    continue

        # 5️⃣ Merge results and sort by similarity
        combined = code_results + text_results
        for r in combined:
         if r["metadata"].get("type") == "repo_summary":
           r["similarity"] += 1.0

        combined.sort(key=lambda x: x["similarity"], reverse=True)
        
        final_results = combined[:top_k]
        print(f"[RETRIEVER] Returning {len(final_results)} results")
        
        # Debug: show top results
        for i, res in enumerate(final_results[:3], 1):
            print(f"  {i}. {res['source']} - {res['metadata'].get('path', 'unknown')[:50]} (sim: {res['similarity']:.3f})")

        return final_results