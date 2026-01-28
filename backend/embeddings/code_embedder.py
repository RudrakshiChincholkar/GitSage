from transformers import AutoTokenizer, AutoModel
import torch

device = "mps" if torch.backends.mps.is_available() else "cpu"
print("Using device:", device)

# Code-aware model
tokenizer = AutoTokenizer.from_pretrained("Salesforce/codet5-base")
model = AutoModel.from_pretrained("Salesforce/codet5-base")
model.eval()

def embed_code(texts: list):
    """
    Convert code snippets into embeddings using CodeT5.
    """
    inputs = tokenizer(
        texts,
        padding=True,
        truncation=True,
        max_length=512,
        return_tensors="pt"
    )

    with torch.no_grad():
        outputs = model(**inputs)

    # Mean pooling
    embeddings = outputs.last_hidden_state.mean(dim=1)

    return embeddings.numpy().tolist()
