from repo_parser import get_repo_details
from github_client import fetch_meta_repodata, fetch_repo_tree
from file_filter import filter_repo_tree
from downloader import download_selected_files

def run_step1(repo_link):
    owner, repo = get_repo_details(repo_link)
    metadata = fetch_meta_repodata(owner, repo)
    branch = metadata["default_branch"]

    tree = fetch_repo_tree(owner, repo, branch)
    important_files = filter_repo_tree(tree)
    downloaded_files = download_selected_files(owner, repo, branch, important_files)

    return downloaded_files
