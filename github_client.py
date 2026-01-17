import requests
from config import GITHUB_PAT

def fetch_meta_repodata(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {
        "Authorization": f"Bearer {GITHUB_PAT}",
        "Accept": "application/vnd.github+json"
    }
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()


def fetch_repo_tree(owner, repo, branch):
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    headers = {
        "Authorization": f"Bearer {GITHUB_PAT}",
        "Accept": "application/vnd.github+json"
    }

    response = requests.get(url, headers=headers, timeout=30)

    if response.status_code == 404 and branch == "main":
        return fetch_repo_tree(owner, repo, "master")

    response.raise_for_status()
    return response.json()["tree"]
