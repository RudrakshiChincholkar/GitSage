from sentence_transformers import SentenceTransformer

# Lightweight & fast model
model = SentenceTransformer("all-MiniLM-L6-v2")


def embed_texts(texts: list) -> list:
    return model.encode(texts).tolist()
