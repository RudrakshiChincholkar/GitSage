import os

# --- File extensions we care about ---

CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".cpp", ".c", ".java"
}

DOC_EXTENSIONS = {
    ".md", ".txt", ".json", ".html", ".css"
}

ALLOWED_EXTENSIONS = CODE_EXTENSIONS | DOC_EXTENSIONS


# --- Folders we should never scan ---

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
    a list of dictionaries:
    {
        file_path: str,
        content: str,
        file_type: "code" | "doc"
    }
    """

    collected_files = []

    for root, dirs, files in os.walk(repo_path):

        # Remove ignored folders from traversal
        dirs[:] = [d for d in dirs if d not in IGNORED_FOLDERS]

        for file in files:
            if not is_valid_file(file):
                continue

            full_path = os.path.join(root, file)
            _, ext = os.path.splitext(file)
            ext = ext.lower()

            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                if not content.strip():
                    continue

                # 🧠 Reduce markdown dominance
                if ext == ".md":
                    content = content[:3000]

                file_type = "code" if ext in CODE_EXTENSIONS else "doc"

                collected_files.append({
                    "file_path": full_path,
                    "content": content,
                    "file_type": file_type
                })

            except Exception as e:
                print(f"Failed to read {full_path}: {e}")

    return collected_files
