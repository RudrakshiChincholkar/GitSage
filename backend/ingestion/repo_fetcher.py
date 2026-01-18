import os
import subprocess
import uuid
import shutil

from ingestion.file_filter import read_repo_files
from embeddings.embedder import embed_texts
from embeddings.chunker import chunk_text
from vectorstore.chroma_client import store_embeddings


def shallow_clone_repo(repo_url: str) -> int:
    repo_id = str(uuid.uuid4())
    base_path = f"/tmp/gitsage_repos/{repo_id}"

    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", "--single-branch", repo_url, base_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        files_data = read_repo_files(base_path)

        all_chunks = []
        metadatas = []
        ids = []

        for i, file in enumerate(files_data):
            chunks = chunk_text(file["content"])

            for j, chunk in enumerate(chunks):
                all_chunks.append(chunk)
                metadatas.append({
                    "repo_url": repo_url,
                    "file_path": file["file_path"]
                })
                ids.append(f"{repo_id}_{i}_{j}")

        embeddings = embed_texts(all_chunks)

        store_embeddings(
            documents=all_chunks,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )

        return len(all_chunks)

    finally:
        if os.path.exists(base_path):
            shutil.rmtree(base_path)
