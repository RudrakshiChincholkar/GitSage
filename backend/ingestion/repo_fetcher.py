import os
import subprocess
import uuid
import shutil

from ingestion.file_filter import read_repo_files
from embeddings.embedder import embed_texts
from embeddings.chunker import chunk_text
from vectorstore.chroma_client import store_embeddings
from ingestion.repo_summary import extract_repo_summary


# ---------------------------------------------------------
# Repo URL normalization
# ---------------------------------------------------------
def normalize_repo_url(url: str) -> str:
    return url.rstrip("/").removesuffix(".git")


# ---------------------------------------------------------
# Repository ingestion
# ---------------------------------------------------------
def ingest_repo(repo_url: str) -> int:
    # Normalize repo URL ONCE
    repo_url = normalize_repo_url(repo_url)

    # Ensure temp directory exists
    os.makedirs("/tmp/gitsage_repos", exist_ok=True)

    repo_id = str(uuid.uuid4())
    base_path = f"/tmp/gitsage_repos/{repo_id}"

    try:
        # Clone repository
        subprocess.run(
            ["git", "clone", "--depth", "1", "--single-branch", repo_url, base_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # 1️⃣ Read repository files
        files_data = read_repo_files(base_path)

        if not files_data:
            print("⚠️ No readable files found in repository.")
            return 0

        # -------------------------------------------------
        # ✅ CRITICAL FIX: make file paths repo-relative
        # -------------------------------------------------
        for f in files_data:
            abs_path = f.get("file_path", "")
            rel_path = os.path.relpath(abs_path, base_path)
            f["file_path"] = rel_path.replace("\\", "/")

        # 2️⃣ Extract high-level repo metadata (languages, manifests)
        # Uses ONLY file paths and manifest contents (no guessing)
        extract_repo_summary(repo_url, files_data)

        # 3️⃣ Sort → code files first, docs later
        files_data = sorted(
            files_data,
            key=lambda f: 0 if f.get("file_type") == "code" else 1
        )

        if not any(f.get("file_type") == "code" for f in files_data):
            print("⚠️ Repository contains no code files. Answers may be limited.")

        all_chunks = []
        metadatas = []
        ids = []

        # 4️⃣ Chunk files (no aggressive filtering)
        for i, file in enumerate(files_data):
            chunks = chunk_text(file.get("content", ""))

            for j, chunk in enumerate(chunks):
                if not chunk.strip():
                    continue

                all_chunks.append(chunk)
                metadatas.append({
                    "repo_url": repo_url,
                    "file_path": file.get("file_path", "unknown"),
                    "file_type": file.get("file_type", "unknown")
                })
                ids.append(f"{repo_id}_{i}_{j}")

        if not all_chunks:
            print("⚠️ No valid text chunks found. Skipping embedding.")
            return 0

        # 5️⃣ Embed and store
        embeddings = embed_texts(all_chunks)

        store_embeddings(
            documents=all_chunks,
            embeddings=embeddings,
            metadatas=metadatas
            # ids are optional; Chroma can auto-generate
        )

        return len(all_chunks)

    finally:
        # Always clean up cloned repo
        if os.path.exists(base_path):
            shutil.rmtree(base_path)
