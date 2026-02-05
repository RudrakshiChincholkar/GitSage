# vectorstore/chroma_store.py
import os
import chromadb
from ingestion.repo_fetcher import normalize_repo_url


class ChromaStore:
    _shared_client = None
    _initialized = False

    def __init__(self, db_path=None):
        # Use a shared client singleton to avoid chromadb initialization conflicts
        if not ChromaStore._initialized:
            ChromaStore._initialize_shared_client(db_path)
        
        self.client = ChromaStore._shared_client
        self.code_collection = self.client.get_or_create_collection(name="gitsage_code")
        self.text_collection = self.client.get_or_create_collection(name="gitsage_text")

    @staticmethod
    def _initialize_shared_client(db_path=None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(base_dir, "chroma_db")
        db_path = os.path.abspath(db_path)

        print(f"[ChromaStore] Using persist_directory={db_path}")

        try:
            from vectorstore.chroma_client import client as shared_client
            ChromaStore._shared_client = shared_client
            print("[ChromaStore] Reusing existing chromadb client from vectorstore.chroma_client")
        except Exception as e:
            print(f"[ChromaStore] Could not import chroma_client: {e}, creating new PersistentClient")
            ChromaStore._shared_client = chromadb.PersistentClient(path=db_path)
        
        ChromaStore._initialized = True

    def add_embeddings(self, embedded_chunks, repo_url: str):
        code_ids, code_docs, code_embeds, code_meta = [], [], [], []
        text_ids, text_docs, text_embeds, text_meta = [], [], [], []

        for i, chunk in enumerate(embedded_chunks):
            base_id = f"{repo_url}_{chunk['path']}_{i}"
            normalized_repo = normalize_repo_url(repo_url)
            metadata = {
                "repo_url": normalized_repo,
                "path": chunk["path"],
                "language": chunk["language"],
                "type": chunk["type"],
            }

            if chunk["type"] == "code":
                code_ids.append(base_id)
                code_docs.append(chunk["text"])
                code_embeds.append(chunk["vector"])
                code_meta.append(metadata)
            else:
                text_ids.append(base_id)
                text_docs.append(chunk["text"])
                text_embeds.append(chunk["vector"])
                text_meta.append(metadata)

        if code_ids:
            self.code_collection.add(
                ids=code_ids,
                documents=code_docs,
                embeddings=code_embeds,
                metadatas=code_meta,
            )

        if text_ids:
            self.text_collection.add(
                ids=text_ids,
                documents=text_docs,
                embeddings=text_embeds,
                metadatas=text_meta,
            )

        print("Code count:", self.code_collection.count())
        print("Text count:", self.text_collection.count())

    def query_code(self, query_vector, top_k=5, repo_url=None):
        query_params = {
            "query_embeddings": [query_vector],
            "n_results": top_k,
            "include": ["documents", "metadatas", "embeddings"],
        }

        if repo_url:
            query_params["where"] = {"repo_url": repo_url}

        return self.code_collection.query(**query_params)

    def query_text(self, query_vector, top_k=5, repo_url=None):
        query_params = {
            "query_embeddings": [query_vector],
            "n_results": top_k,
            "include": ["documents", "metadatas", "embeddings"],
        }

        if repo_url:
            query_params["where"] = {"repo_url": repo_url}

        return self.text_collection.query(**query_params)

    def inspect_code_embeddings(self, limit=1):
        return self.code_collection.get(
            include=["embeddings", "documents", "metadatas"],
            limit=limit,
        )

    def inspect_text_embeddings(self, limit=1):
        return self.text_collection.get(
            include=["embeddings", "documents", "metadatas"],
            limit=limit,
        )

    def inspect_embeddings(self, limit=1):
        return {
            "code": self.inspect_code_embeddings(limit),
            "text": self.inspect_text_embeddings(limit),
        }
