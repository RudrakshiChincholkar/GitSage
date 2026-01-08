import requests
import os


def fetch_repo_metadata(repo_url: str) -> dict:
    """
    Fetch basic GitHub repository metadata using GitHub API.
    """

    token = os.getenv("GITHUB_TOKEN")

    headers = {
        "Authorization": f"token {token}"
    }

    api_url = repo_url.replace(
        "https://github.com/",
        "https://api.github.com/repos/"
    )

    response = requests.get(api_url, headers=headers)

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
