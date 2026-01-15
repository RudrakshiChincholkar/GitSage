from sentence_transformers import SentenceTransformer

# Lightweight, fast model for natural language
model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_texts(texts: list):
    """
    Convert a list of text chunks into embeddings.
    """
    return model.encode(texts).tolist()
