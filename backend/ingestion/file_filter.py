import os

# File extensions we care about
ALLOWED_EXTENSIONS = {
    ".py", ".js", ".ts", ".cpp", ".c", ".java",
    ".md", ".txt", ".json", ".html", ".css"
}

# Folders we should never scan
IGNORED_FOLDERS = {
    ".git", "node_modules", "dist", "build",
    "__pycache__", ".venv", "env", ".idea", ".vscode"
}


def is_valid_file(filename: str) -> bool:
    """Check if file has a valid extension."""
    _, ext = os.path.splitext(filename)
    return ext.lower() in ALLOWED_EXTENSIONS


def read_repo_files(repo_path: str) -> list:
    """
    Walk through a repo folder and return
    a list of {file_path, content} dictionaries.
    """

    collected_files = []

    for root, dirs, files in os.walk(repo_path):

        # Remove ignored folders from traversal
        dirs[:] = [d for d in dirs if d not in IGNORED_FOLDERS]

        for file in files:
            if not is_valid_file(file):
                continue

            full_path = os.path.join(root, file)

            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                if content.strip():
                    collected_files.append({
                        "file_path": full_path,
                        "content": content
                    })

            except Exception as e:
                print(f"Failed to read {full_path}: {e}")

    return collected_files
