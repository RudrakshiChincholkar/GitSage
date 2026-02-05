from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModel
import torch

class QueryEmbedder:
    def __init__(self):
        # Must match indexing models
        self.text_model = SentenceTransformer("all-MiniLM-L6-v2")

        self.code_tokenizer = AutoTokenizer.from_pretrained("Salesforce/codet5-base")
        self.code_model = AutoModel.from_pretrained("Salesforce/codet5-base")

    def embed_text_query(self, query):
        return self.text_model.encode(query).tolist()

    def embed_code_query(self, query):
        inputs = self.code_tokenizer(
            query,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=512
        )

        with torch.no_grad():
            outputs = self.code_model.encoder(**inputs)

        vector = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
        return vector.tolist()
