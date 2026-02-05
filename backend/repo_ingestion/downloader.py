import asyncio
import aiohttp
from typing import Dict, List
from config import GITHUB_PAT


async def download_file(session: aiohttp.ClientSession, owner: str, repo: str, 
                       branch: str, file: dict) -> tuple:
    """
    Download a single file asynchronously.
    
    Returns:
        Tuple of (file_path, content) or (file_path, None) on failure
    """
    file_path = file["path"]
    raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{file_path}"
    
    try:
        async with session.get(raw_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
            if response.status == 200:
                content = await response.text()
                return (file_path, content)
            else:
                print(f"Failed to download: {file_path} (status: {response.status})")
                return (file_path, None)
    except Exception as e:
        print(f"Error downloading {file_path}: {e}")
        return (file_path, None)


async def download_files_async(owner: str, repo: str, branch: str, 
                               filtered_files: List[dict]) -> Dict[str, str]:
    """
    Download multiple files concurrently using async HTTP.
    
    Args:
        owner: GitHub repository owner
        repo: Repository name
        branch: Branch name
        filtered_files: List of file dicts with 'path' key
    
    Returns:
        Dict mapping file_path to file_content
    """
    headers = {"Authorization": f"Bearer {GITHUB_PAT}"}
    
    async with aiohttp.ClientSession(headers=headers) as session:
        # Create tasks for all files
        tasks = [
            download_file(session, owner, repo, branch, file)
            for file in filtered_files
        ]
        
        # Download all files concurrently
        results = await asyncio.gather(*tasks)
    
    # Filter out failed downloads
    downloaded_files = {
        path: content 
        for path, content in results 
        if content is not None
    }
    
    print(f"✓ Downloaded {len(downloaded_files)}/{len(filtered_files)} files")
    return downloaded_files


def download_selected_files(owner: str, repo: str, branch: str, 
                           filtered_files: List[dict]) -> Dict[str, str]:
    """
    Synchronous wrapper for async download function.
    Creates a new event loop to avoid conflicts with FastAPI's loop.
    """
    # Create a fresh event loop (won't conflict with FastAPI's loop)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(
            download_files_async(owner, repo, branch, filtered_files)
        )
        return result
    finally:
        loop.close()