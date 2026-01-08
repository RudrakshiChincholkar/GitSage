from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import subprocess
import uuid
import shutil

# Load environment variables from .env
load_dotenv()

app = FastAPI()

# Request Model 
class RepoRequest(BaseModel):
    repo_url: str


# Ingest Repo Endpoint 
@app.post("/ingest-repo")
def ingest_repo(req: RepoRequest):
    print("INGESTING REPO:", req.repo_url)

    # Create a unique temp directory
    repo_id = str(uuid.uuid4())
    base_path = f"/tmp/gitsage_repos/{repo_id}"

    try:
        # Shallow clone the repo
        subprocess.run(
            [
                "git",
                "clone",
                "--depth",
                "1",
                "--single-branch",
                req.repo_url,
                base_path
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        print("CLONED INTO:", base_path)

        # Walk files to confirm clone worked
        file_count = 0
        for root, dirs, files in os.walk(base_path):
            # ignore .git directory
            if ".git" in dirs:
                dirs.remove(".git")
            file_count += len(files)

        print("TOTAL FILES:", file_count)

        return {
            "message": "Repo cloned successfully",
            "file_count": file_count
        }

    except subprocess.CalledProcessError as e:
        return {
            "error": "Git clone failed",
            "details": e.stderr.decode()
        }

    finally:
        # Cleanup: delete cloned repo
        if os.path.exists(base_path):
            shutil.rmtree(base_path)
            print("DELETED:", base_path)
