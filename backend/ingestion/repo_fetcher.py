import os
import subprocess
import uuid
import shutil


def shallow_clone_repo(repo_url: str) -> int:

    repo_id = str(uuid.uuid4())
    base_path = f"/tmp/gitsage_repos/{repo_id}"

    try:
        subprocess.run(
            [
                "git",
                "clone",
                "--depth",
                "1",
                "--single-branch",
                repo_url,
                base_path
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        file_count = 0
        for root, dirs, files in os.walk(base_path):
            if ".git" in dirs:
                dirs.remove(".git")
            file_count += len(files)

        return file_count

    finally:
        if os.path.exists(base_path):
            shutil.rmtree(base_path)
