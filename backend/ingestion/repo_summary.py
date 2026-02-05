import os
import json
from typing import Dict, List, Set

from ingestion.file_filter import CODE_EXTENSIONS


# ---------------------------------------------------------
# In-memory store: normalized repo_url -> summary text
# ---------------------------------------------------------
_REPO_SUMMARIES: Dict[str, str] = {}


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
def _detect_languages(file_paths: List[str]) -> Set[str]:
    """
    Infer programming languages purely from file extensions.
    Conservative by design: no guessing beyond extensions.
    """
    languages: Set[str] = set()

    for path in file_paths:
        _, ext = os.path.splitext(path)
        ext = ext.lower()

        if ext not in CODE_EXTENSIONS:
            continue

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
        # Intentionally no guessing beyond this

    return languages


def _detect_top_level_dirs(file_paths: List[str]) -> Set[str]:
    """
    Extract top-level directory names from file paths.
    Example: src/utils/file.py -> src
    """
    dirs: Set[str] = set()

    for path in file_paths:
        parts = path.strip("/").split("/")
        if len(parts) > 1:
            dirs.add(parts[0])

    return dirs


def _parse_package_json(content: str) -> Set[str]:
    """
    Extract dependency names from a package.json file.
    """
    libs: Set[str] = set()

    try:
        data = json.loads(content)
    except Exception:
        return libs

    for key in ("dependencies", "devDependencies", "peerDependencies"):
        section = data.get(key)
        if isinstance(section, dict):
            libs.update(section.keys())

    return libs


def _parse_requirements_txt(content: str) -> Set[str]:
    """
    Extract dependency names from requirements.txt-style files.
    """
    libs: Set[str] = set()

    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        for sep in ("==", ">=", "<=", "~=", ">", "<"):
            if sep in line:
                line = line.split(sep, 1)[0].strip()
                break

        if line:
            libs.add(line)

    return libs


# ---------------------------------------------------------
# Public API
# ---------------------------------------------------------
def extract_repo_summary(repo_url: str, files_data: List[Dict]) -> None:
    """
    Build a conservative, evidence-based repository summary.

    Sources of truth:
    - File extensions → languages
    - package.json / requirements.txt → dependencies
    - File paths → directory structure

    NO semantic guessing.
    NO domain assumptions.
    """

    file_paths = [f.get("file_path", "") for f in files_data]

    # Structural signals
    languages = _detect_languages(file_paths)
    top_dirs = _detect_top_level_dirs(file_paths)

    # Dependency signals
    libs: Set[str] = set()
    for f in files_data:
        path = f.get("file_path", "").lower()
        content = f.get("content", "")

        if path.endswith("package.json"):
            libs.update(_parse_package_json(content))
        elif path.endswith("requirements.txt"):
            libs.update(_parse_requirements_txt(content))

    # If nothing reliable is found, do not store a summary
    if not languages and not libs and not top_dirs:
        return

    lines: List[str] = [
        "Repository summary (from file types, structure, and manifests only):"
    ]

    if languages:
        lines.append("Languages: " + ", ".join(sorted(languages)))

    if top_dirs:
        lines.append("Top-level directories: " + ", ".join(sorted(top_dirs)))

    if libs:
        lines.append(
            "Dependencies / libraries (from manifests): "
            + ", ".join(sorted(libs))
        )

    _REPO_SUMMARIES[repo_url] = "\n".join(lines)


def get_repo_summary(repo_url: str) -> str | None:
    """
    Return the previously extracted repository summary, if any.
    """
    return _REPO_SUMMARIES.get(repo_url)
