# ingestion/repo_summary.py
import os
import json
from typing import Dict, List, Set

# Simple in-memory store: repo_url -> summary text
_REPO_SUMMARIES: Dict[str, str] = {}


def _detect_languages(file_paths: List[str]) -> Set[str]:
    """Infer languages from file extensions."""
    languages: Set[str] = set()
    
    for path in file_paths:
        _, ext = os.path.splitext(path)
        ext = ext.lower()
        
        # Map extensions to languages
        if ext == ".py":
            languages.add("Python")
        elif ext in {".js", ".jsx"}:
            languages.add("JavaScript")
        elif ext in {".ts", ".tsx"}:
            languages.add("TypeScript")
        elif ext == ".java":
            languages.add("Java")
        elif ext in {".cpp", ".cc", ".cxx"}:
            languages.add("C++")
        elif ext == ".c":
            languages.add("C")
        elif ext == ".go":
            languages.add("Go")
        elif ext == ".rs":
            languages.add("Rust")
        elif ext == ".rb":
            languages.add("Ruby")
        elif ext == ".php":
            languages.add("PHP")
    
    return languages


def _parse_package_json(content: str) -> Set[str]:
    """Extract dependency names from package.json."""
    libs: Set[str] = set()
    
    try:
        data = json.loads(content)
    except Exception:
        return libs
    
    # Check all dependency sections
    for key in ("dependencies", "devDependencies", "peerDependencies"):
        section = data.get(key) or {}
        if isinstance(section, dict):
            libs.update(section.keys())
    
    return libs


def _parse_requirements_txt(content: str) -> Set[str]:
    """Extract package names from requirements.txt."""
    libs: Set[str] = set()
    
    for line in content.splitlines():
        line = line.strip()
        
        # Skip comments and empty lines
        if not line or line.startswith("#"):
            continue
        
        # Remove version specifiers
        for sep in ("==", ">=", "<=", "~=", ">", "<", "["):
            if sep in line:
                line = line.split(sep, 1)[0].strip()
                break
        
        if line:
            libs.add(line)
    
    return libs


def extract_repo_summary(repo_url: str, downloaded_files: Dict[str, str]) -> None:
    """
    Extract high-level repository metadata from downloaded files.
    
    Args:
        repo_url: The repository URL
        downloaded_files: Dict of {file_path: file_content}
    
    Stores summary in memory for later retrieval.
    """
    # Get all file paths
    file_paths = list(downloaded_files.keys())
    
    # Detect languages from file extensions
    languages = _detect_languages(file_paths)
    
    # Extract dependencies from manifest files
    libs: Set[str] = set()
    
    for path, content in downloaded_files.items():
        path_lower = path.lower()
        
        if path_lower.endswith("package.json"):
            libs.update(_parse_package_json(content))
        elif path_lower.endswith("requirements.txt"):
            libs.update(_parse_requirements_txt(content))
    
    # Only create summary if we found metadata
    if not languages and not libs:
        return
    
    # Build summary text
    lines = ["Repository summary (from file types and manifests):"]
    
    if languages:
        lines.append("Languages: " + ", ".join(sorted(languages)))
    
    if libs:
        # Limit to top 20 dependencies to avoid huge summaries
        top_libs = sorted(libs)[:20]
        lines.append("Dependencies: " + ", ".join(top_libs))
    
    # Store in memory
    _REPO_SUMMARIES[repo_url] = "\n".join(lines)


def get_repo_summary(repo_url: str) -> str:
    """
    Retrieve a previously extracted summary.
    
    Args:
        repo_url: The repository URL
    
    Returns:
        Summary string or empty string if not found
    """
    return _REPO_SUMMARIES.get(repo_url, "")
