"""
Global singleton manager for embedding models.
Ensures models are loaded exactly once and reused across all requests.

This manager supports both:
1. Dual-model approach (CodeT5 + MiniLM) - current implementation
2. Single-model approach (future optimization)
"""
from typing import Optional
from embeddings.code_embedder_new import CodeEmbedder
from embeddings.sentence_embedder import SentenceEmbedder


class EmbedderManager:
    """
    Singleton manager that holds references to embedder instances.
    These instances are created once and reused for the lifetime of the application.
    """
    _instance: Optional['EmbedderManager'] = None
    _code_embedder: Optional[CodeEmbedder] = None
    _text_embedder: Optional[SentenceEmbedder] = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(self):
        """
        Lazy initialization of models.
        Call this at application startup or on first use.
        """
        if not self._initialized:
            print("[EmbedderManager] Initializing models (one-time operation)...")
            self._code_embedder = CodeEmbedder()
            self._text_embedder = SentenceEmbedder()
            self._initialized = True
            print("[EmbedderManager] ✓ Models loaded and ready")

    @property
    def code_embedder(self) -> CodeEmbedder:
        if not self._initialized:
            self.initialize()
        return self._code_embedder

    @property
    def text_embedder(self) -> SentenceEmbedder:
        if not self._initialized:
            self.initialize()
        return self._text_embedder


# Global singleton instance
_embedder_manager = EmbedderManager()


def get_code_embedder() -> CodeEmbedder:
    """Get the shared code embedder instance."""
    return _embedder_manager.code_embedder


def get_text_embedder() -> SentenceEmbedder:
    """Get the shared text embedder instance."""
    return _embedder_manager.text_embedder


def get_embedder():
    """
    For compatibility with single-model approach.
    Returns the text embedder (can be used for both code and text).
    """
    return _embedder_manager.text_embedder


def initialize_embedders():
    """
    Pre-initialize all embedders.
    Call this at application startup to avoid first-request latency.
    """
    _embedder_manager.initialize()