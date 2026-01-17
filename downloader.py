import requests
from config import GITHUB_PAT

def download_selected_files(owner, repo, branch, filtered_files):
    headers = {"Authorization": f"Bearer {GITHUB_PAT}"}
    downloaded_files = {}

    for file in filtered_files:
        file_path = file["path"]
        raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{file_path}"

        response = requests.get(raw_url, headers=headers, timeout=30)

        if response.status_code == 200:
            downloaded_files[file_path] = response.text
        else:
            print(f"Failed to download: {file_path}")

    return downloaded_files
