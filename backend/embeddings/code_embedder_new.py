from typing import List

import torch
from transformers import AutoModel, AutoTokenizer


class CodeEmbedder:
    """
    Wrapper around a shared code embedding model.

    The underlying transformer model and tokenizer are loaded once per
    process and reused across calls to avoid per-request initialization
    overhead.
    """

    _tokenizer: AutoTokenizer | None = None
    _model: AutoModel | None = None
    _model_name: str = "Salesforce/codet5-base"

    def __init__(self, model_name: str | None = None):
        if model_name is not None and model_name != self._model_name:
            # If a different model name is ever requested, update the
            # class-level reference and force a reload exactly once.
            CodeEmbedder._model_name = model_name
            CodeEmbedder._tokenizer = None
            CodeEmbedder._model = None

        if CodeEmbedder._tokenizer is None or CodeEmbedder._model is None:
            CodeEmbedder._tokenizer = AutoTokenizer.from_pretrained(self._model_name)
            CodeEmbedder._model = AutoModel.from_pretrained(self._model_name)
            CodeEmbedder._model.eval()  # production best practice

    def embed(self, texts: List[str]) -> List[list[float]]:
        """
        Embed a list of code strings into vector representations.

        Args:
            texts: List of source code snippets.

        Returns:
            List of embedding vectors (as Python lists of floats).
        """
        assert CodeEmbedder._tokenizer is not None, "Code tokenizer not initialized"
        assert CodeEmbedder._model is not None, "Code model not initialized"

        inputs = CodeEmbedder._tokenizer(
            texts,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=512,
        )

        with torch.no_grad():
            encoder_outputs = CodeEmbedder._model.encoder(
                input_ids=inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
            )

        # Mean pooling over token dimension
        embeddings = encoder_outputs.last_hidden_state.mean(dim=1)

        return embeddings.cpu().tolist()
