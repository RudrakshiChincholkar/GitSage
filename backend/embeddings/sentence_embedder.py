from sentence_transformers import SentenceTransformer

class SentenceEmbedder:
    def __init__(self, model_name = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed(self, texts):

        # input: List[str]       - give me list of sentences
        # returns: List[List[float]]    - I'll give you list of lists which are numbers(vectors)

        return self.model.encode(texts, convert_to_numpy=True).tolist()