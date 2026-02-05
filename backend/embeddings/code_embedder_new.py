from transformers import AutoTokenizer, AutoModel
import torch

class CodeEmbedder:
    def __init__(self, model_name="Salesforce/codet5-base"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.eval()  # production best practice

    def embed(self, texts):
        inputs = self.tokenizer(
            texts,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=512
        )

        with torch.no_grad():
            encoder_outputs = self.model.encoder(
                input_ids=inputs["input_ids"],
                attention_mask=inputs["attention_mask"]
            )

        # Mean pooling over token dimension
        embeddings = encoder_outputs.last_hidden_state.mean(dim=1)

        return embeddings.cpu().tolist()
