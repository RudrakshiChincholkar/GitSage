from fastapi import FastAPI
from dotenv import load_dotenv

from ingestion.models import RepoRequest
from ingestion.repo_fetcher import shallow_clone_repo
from ingestion.github_client import fetch_repo_metadata

load_dotenv()

app = FastAPI()


@app.post("/ingest-repo")
def ingest_repo(req: RepoRequest):
    print("INGESTING REPO:", req.repo_url)

    try:
        #Fetch metadata
        metadata = fetch_repo_metadata(req.repo_url)

        #Shallow clone + cleanup
        file_count = shallow_clone_repo(req.repo_url)

        return {
            "message": "Repo ingested successfully",
            "metadata": metadata,
            "file_count": file_count
        }

    except Exception as e:
        return {
            "error": "Repo ingestion failed",
            "details": str(e)
        }
