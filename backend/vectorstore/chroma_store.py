# vectorstore/chroma_store.py
import os
import uuid

import chromadb

from ingestion.repo_fetcher import normalize_repo_url


class ChromaStore:
    """
    Centralized access to ChromaDB collections used by GitSage.

    - Uses a shared PersistentClient instance (singleton) to avoid repeated
      initialization and to ensure embeddings are written to a single
      persistent store.
    - Maintains separate collections for code, text, and repository-level
      ingestion metadata.
    """

    _shared_client = None
    _initialized = False

    def __init__(self, db_path: str | None = None):
        # Use a shared client singleton to avoid chromadb initialization conflicts
        if not ChromaStore._initialized:
            ChromaStore._initialize_shared_client(db_path)

        self.client = ChromaStore._shared_client
        self.code_collection = self.client.get_or_create_collection(name="gitsage_code")
        self.text_collection = self.client.get_or_create_collection(name="gitsage_text")
        # Tracks which repos (and which versions) have been ingested.
        self.repo_collection = self.client.get_or_create_collection(name="gitsage_repo_index")

    @staticmethod
    def _initialize_shared_client(db_path: str | None = None) -> None:
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

    # ------------------------------------------------------------------
    # Embedding storage
    # ------------------------------------------------------------------
    def add_embeddings(self, embedded_chunks, repo_url: str):
        """
        Persist a batch of embedded chunks into code/text collections.

        Each chunk is expected to have:
            - path
            - language
            - type ("code" | "text")
            - text
            - vector
        """
        code_ids, code_docs, code_embeds, code_meta = [], [], [], []
        text_ids, text_docs, text_embeds, text_meta = [], [], [], []

        normalized_repo = normalize_repo_url(repo_url)

        for i, chunk in enumerate(embedded_chunks):
            # Ensure text payload is always a plain string for Chroma
            text = chunk.get("text", "")
            if isinstance(text, list):
                text = "\n".join(str(t) for t in text)
            else:
                text = str(text)

            base_id = f"{normalized_repo}_{chunk['path']}_{i}"
            metadata = {
                "repo_url": normalized_repo,
                "path": chunk["path"],
                "language": chunk["language"],
                "type": chunk["type"],
            }

            if chunk["type"] == "code":
                code_ids.append(base_id)
                code_docs.append(text)
                code_embeds.append(chunk["vector"])
                code_meta.append(metadata)
            else:
                text_ids.append(base_id)
                text_docs.append(text)
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

    # ------------------------------------------------------------------
    # Repository ingestion index (to avoid re-embedding unchanged repos)
    # ------------------------------------------------------------------
    def is_repo_ingested(self, repo_url: str, repo_version: str | None) -> bool:
        """
        Check whether a given repo/version combination has already been ingested.

        repo_version is typically derived from GitHub metadata (e.g. `pushed_at`).
        """
        if not repo_version:
            return False

        normalized_repo = normalize_repo_url(repo_url)

        # Some Chroma versions require a specific filter syntax for `where` on
        # .get(). To remain maximally compatible and avoid subtle validation
        # errors, we simply scan a bounded number of metadata entries in this
        # small index collection.
        existing = self.repo_collection.get(limit=10000, include=["metadatas"])
        metadatas = existing.get("metadatas") or []

        for meta in metadatas:
            if not isinstance(meta, dict):
                continue
            if meta.get("repo_url") == normalized_repo and meta.get("repo_version") == repo_version:
                return True

        return False

    def mark_repo_ingested(self, repo_url: str, repo_version: str | None) -> None:
        """
        Record that a given repo/version has completed ingestion.
        """
        if not repo_version:
            return

        normalized_repo = normalize_repo_url(repo_url)
        doc_id = f"{normalized_repo}:{repo_version}"

        self.repo_collection.add(
            ids=[doc_id],
            documents=[f"Repo {normalized_repo} at version {repo_version}"],
            metadatas=[
                {
                    "repo_url": normalized_repo,
                    "repo_version": repo_version,
                }
            ],
        )

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------
    def query_code(self, query_vector, top_k: int = 5, repo_url: str | None = None):
        query_params = {
            "query_embeddings": [query_vector],
            "n_results": top_k,
            "include": ["documents", "metadatas", "embeddings"],
        }

        if repo_url:
            query_params["where"] = {"repo_url": normalize_repo_url(repo_url)}

        return self.code_collection.query(**query_params)

    def query_text(self, query_vector, top_k: int = 5, repo_url: str | None = None):
        query_params = {
            "query_embeddings": [query_vector],
            "n_results": top_k,
            "include": ["documents", "metadatas", "embeddings"],
        }

        if repo_url:
            query_params["where"] = {"repo_url": normalize_repo_url(repo_url)}

        return self.text_collection.query(**query_params)

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------
    def inspect_code_embeddings(self, limit: int = 1):
        return self.code_collection.get(
            include=["embeddings", "documents", "metadatas"],
            limit=limit,
        )

    def inspect_text_embeddings(self, limit: int = 1):
        return self.text_collection.get(
            include=["embeddings", "documents", "metadatas"],
            limit=limit,
        )

    def inspect_embeddings(self, limit: int = 1):
        return {
            "code": self.inspect_code_embeddings(limit),
            "text": self.inspect_text_embeddings(limit),
        }
