import requests
import os
from urllib.parse import urlparse

def fetch_repo_metadata(repo_url: str) -> dict:
    token = os.getenv("GITHUB_TOKEN")

    headers = {
        "Authorization": f"token {token}"
    }

    parsed = urlparse(repo_url)
    parts = parsed.path.strip("/").replace(".git", "").split("/")

    owner, repo = parts[0], parts[1]

    api_url = f"https://api.github.com/repos/{owner}/{repo}"

    print("FINAL API URL:", api_url)

    response = requests.get(api_url, headers=headers)

    print("STATUS:", response.status_code)

    if response.status_code != 200:
        raise Exception("Failed to fetch repository metadata")

    data = response.json()

    return {
        "name": data.get("full_name"),
        "stars": data.get("stargazers_count"),
        "forks": data.get("forks_count"),
        "language": data.get("language"),
        "description": data.get("description")
    }
