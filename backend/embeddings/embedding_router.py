from embeddings.sentence_embedder import SentenceEmbedder
from embeddings.code_embedder_new import CodeEmbedder  # Use new one

class EmbeddingRouter:
    def __init__(self):
        self.text_embedder = SentenceEmbedder()
        self.code_embedder = CodeEmbedder()

    def route_and_embed(self,chunks):

        doc_chunks = []
        code_chunks = []
        
        # separating code and text
        for c in chunks :
            if c["type"]== "code":
                code_chunks.append(c)
            elif c["type"] == "text":
                doc_chunks.append(c)

        doc_vectors = self.text_embedder.embed([c["text"] for c in doc_chunks]) if doc_chunks else []
        code_vectors = self.code_embedder.embed([c["text"] for c in code_chunks]) if code_chunks else []


        embedded = []

        for chunk, vector in zip(doc_chunks, doc_vectors):
            embedded.append({**chunk, "vector": vector})

        for chunk, vector in zip(code_chunks, code_vectors):
            embedded.append({**chunk, "vector": vector})

        return embedded
        