from typing import Any, List

from embeddings.sentence_embedder import SentenceEmbedder
from embeddings.code_embedder_new import CodeEmbedder  # Use new one


class EmbeddingRouter:
    def __init__(self):
        self.text_embedder = SentenceEmbedder()
        self.code_embedder = CodeEmbedder()

    @staticmethod
    def _normalize_text(value: Any) -> str:
        """
        Ensure every chunk's 'text' field is a single string.

        Some chunkers may produce lists of lines; SentenceTransformer and
        Chroma both expect plain strings, so we join lists with newlines and
        coerce everything else to str.
        """
        if isinstance(value, list):
            return "\n".join(str(v) for v in value)
        return str(value)

    def route_and_embed(self, chunks: List[dict]):
        doc_chunks: List[dict] = []
        code_chunks: List[dict] = []

        # Normalize text and separate code vs text chunks
        for c in chunks:
            c = dict(c)  # shallow copy in case callers reuse dicts
            c["text"] = self._normalize_text(c.get("text", ""))

            if c.get("type") == "code":
                code_chunks.append(c)
            elif c.get("type") == "text":
                doc_chunks.append(c)

        doc_vectors = (
            self.text_embedder.embed([c["text"] for c in doc_chunks]) if doc_chunks else []
        )
        code_vectors = (
            self.code_embedder.embed([c["text"] for c in code_chunks]) if code_chunks else []
        )

        embedded: List[dict] = []

        for chunk, vector in zip(doc_chunks, doc_vectors):
            embedded.append({**chunk, "vector": vector})

        for chunk, vector in zip(code_chunks, code_vectors):
            embedded.append({**chunk, "vector": vector})

        return embedded
        