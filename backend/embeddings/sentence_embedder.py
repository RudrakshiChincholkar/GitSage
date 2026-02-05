from sentence_transformers import SentenceTransformer
from typing import List


class SentenceEmbedder:
    """
    Thin wrapper around a shared SentenceTransformer instance.

    The underlying model is loaded once per process and reused across
    all embed() calls to avoid expensive re-initialization on each
    request.
    """

    _model: SentenceTransformer | None = None
    _model_name: str = "all-MiniLM-L6-v2"

    def __init__(self, model_name: str | None = None):
        if model_name is not None and model_name != self._model_name:
            # If a different model name is ever requested, update the
            # class-level reference and force a reload exactly once.
            SentenceEmbedder._model_name = model_name
            SentenceEmbedder._model = None

        if SentenceEmbedder._model is None:
            SentenceEmbedder._model = SentenceTransformer(self._model_name)

    def embed(self, texts: List[str]) -> List[list[float]]:
        """
        Embed a list of strings into vector representations.

        Args:
            texts: List of input strings.

        Returns:
            List of embedding vectors (as Python lists of floats).
        """
        assert SentenceEmbedder._model is not None, "SentenceTransformer model not initialized"
        return SentenceEmbedder._model.encode(texts, convert_to_numpy=True).tolist()