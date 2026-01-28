import os  # ADDED
import json  # ADDED
from typing import Dict, List, Set  # ADDED

from ingestion.file_filter import CODE_EXTENSIONS  # ADDED


# Simple in-memory store: normalized repo_url -> summary text  # ADDED
_REPO_SUMMARIES: Dict[str, str] = {}  # ADDED


def _detect_languages(file_paths: List[str]) -> Set[str]:  # ADDED
    """Infer languages purely from file extensions."""  # ADDED
    languages: Set[str] = set()  # ADDED
    for path in file_paths:  # ADDED
        _, ext = os.path.splitext(path)  # ADDED
        ext = ext.lower()  # ADDED
        if ext not in CODE_EXTENSIONS:  # ADDED
            continue  # ADDED
        if ext == ".py":  # ADDED
            languages.add("Python")  # ADDED
        elif ext in {".js", ".jsx"}:  # ADDED
            languages.add("JavaScript")  # ADDED
        elif ext in {".ts", ".tsx"}:  # ADDED
            languages.add("TypeScript")  # ADDED
        elif ext in {".java"}:  # ADDED
            languages.add("Java")  # ADDED
        elif ext in {".cpp", ".cc", ".cxx"}:  # ADDED
            languages.add("C++")  # ADDED
        elif ext == ".c":  # ADDED
            languages.add("C")  # ADDED
        # Other extensions can be added later, but we avoid guessing.  # ADDED
    return languages  # ADDED


def _parse_package_json(content: str) -> Set[str]:  # ADDED
    """Return dependency names from a package.json string."""  # ADDED
    libs: Set[str] = set()  # ADDED
    try:  # ADDED
        data = json.loads(content)  # ADDED
    except Exception:  # ADDED
        return libs  # ADDED
    for key in ("dependencies", "devDependencies", "peerDependencies"):  # ADDED
        section = data.get(key) or {}  # ADDED
        if isinstance(section, dict):  # ADDED
            libs.update(section.keys())  # ADDED
    return libs  # ADDED


def _parse_requirements_txt(content: str) -> Set[str]:  # ADDED
    """Return requirement names from a requirements.txt-style file."""  # ADDED
    libs: Set[str] = set()  # ADDED
    for line in content.splitlines():  # ADDED
        line = line.strip()  # ADDED
        if not line or line.startswith("#"):  # ADDED
            continue  # ADDED
        # Split on common version specifiers without interpreting them.  # ADDED
        for sep in ("==", ">=", "<=", "~=", ">", "<"):  # ADDED
            if sep in line:  # ADDED
                line = line.split(sep, 1)[0].strip()  # ADDED
                break  # ADDED
        if line:  # ADDED
            libs.add(line)  # ADDED
    return libs  # ADDED


def extract_repo_summary(repo_url: str, files_data: List[Dict]) -> None:  # ADDED
    """  # ADDED
    Build a conservative metadata summary from concrete repo evidence only.  # ADDED
    - Languages are inferred from file extensions.  # ADDED
    - Framework / stack hints come from manifest files (package.json, requirements.txt).  # ADDED
    The summary is stored in-memory and can be used during QA.  # ADDED
    """  # ADDED
    file_paths = [f.get("file_path", "") for f in files_data]  # ADDED
    languages = _detect_languages(file_paths)  # ADDED

    libs: Set[str] = set()  # ADDED
    for f in files_data:  # ADDED
        path = f.get("file_path", "")  # ADDED
        content = f.get("content", "")  # ADDED
        lower_path = path.lower()  # ADDED

        if lower_path.endswith("package.json"):  # ADDED
            libs.update(_parse_package_json(content))  # ADDED
        elif lower_path.endswith("requirements.txt"):  # ADDED
            libs.update(_parse_requirements_txt(content))  # ADDED

    if not languages and not libs:  # ADDED
        # No reliable metadata; leave behavior unchanged.  # ADDED
        return  # ADDED

    lines = ["Repository summary (from file types and manifests only):"]  # ADDED
    if languages:  # ADDED
        lines.append("Languages: " + ", ".join(sorted(languages)))  # ADDED
    if libs:  # ADDED
        lines.append("Dependencies / libraries (from manifests): " + ", ".join(sorted(libs)))  # ADDED

    _REPO_SUMMARIES[repo_url] = "\n".join(lines)  # ADDED


def get_repo_summary(repo_url: str) -> str | None:  # ADDED
    """Return a previously extracted summary, if any."""  # ADDED
    return _REPO_SUMMARIES.get(repo_url)  # ADDED


