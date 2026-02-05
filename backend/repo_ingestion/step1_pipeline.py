# this file is for fetching repo details(metadata, tree structure, branch) and then 
# after filtering the files we can download the ones we actually find important  


from repo_ingestion.fetcher import get_repo_details
from repo_ingestion.fetcher import fetch_meta_repodata, fetch_repo_tree
from repo_ingestion.before_file_download_filter import filter_repo_tree
from repo_ingestion.downloader import download_files_async, download_selected_files
from repo_ingestion.repo_summary_new import extract_repo_summary


async def run_step1_async(repo_link):
    """
    Async version of step1 pipeline.
    Use this when called from async contexts (FastAPI endpoints).
    """
    owner, repo = get_repo_details(repo_link)
    metadata = fetch_meta_repodata(owner, repo)
    branch = metadata["default_branch"]

    tree = fetch_repo_tree(owner, repo, branch)
    important_files = filter_repo_tree(tree)
    
    # Use async download directly
    downloaded_files = await download_files_async(owner, repo, branch, important_files)

    extract_repo_summary(repo_link, downloaded_files)

    return downloaded_files


def run_step1(repo_link):
    """
    Synchronous version - for backward compatibility if needed.
    Uses the synchronous wrapper in downloader.py
    """
    owner, repo = get_repo_details(repo_link)
    metadata = fetch_meta_repodata(owner, repo)
    branch = metadata["default_branch"]

    tree = fetch_repo_tree(owner, repo, branch)
    important_files = filter_repo_tree(tree)
    downloaded_files = download_selected_files(owner, repo, branch, important_files)

    extract_repo_summary(repo_link, downloaded_files)

    return downloaded_files