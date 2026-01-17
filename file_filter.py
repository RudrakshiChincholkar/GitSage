import os

def filter_repo_tree(tree_structure):
    valuable_files = []

    for item in tree_structure:
        if item.get("type") == "blob":
            path = item.get("path")
            size = item.get("size", 0)

            if is_file_valuable(path, size):
                valuable_files.append({
                    "path" : path,
                    "size" : size
                })
    return valuable_files  


def is_file_valuable(path, size_in_bytes):
    path_parts = path.lower().split('/')
    filename = path_parts[-1]
    extension = os.path.splitext(filename)[1]

    JUNK_DIRS = {
        'node_modules', '.git', '.github', '__pycache__', 
        'venv', 'env', 'dist', 'build', 'target', '.vscode', '.idea',
        '.mvn', '.gradle', 'bower_components'
    }
    if any(part in JUNK_DIRS for part in path_parts):
        return False

    JUNK_EXT = {
        '.png','.jpg','.jpeg','.gif','.ico','.svg',
        '.mp4','.mov','.mp3',
        '.pdf','.zip','.tar','.gz','.7z',
        '.exe','.bin','.dll','.pyc','.o','.so',
        '.ttf','.woff','.woff2',
        '.lock','.db','.sqlite','.mv.db',
        '.p12','.pem','.crt','.key'
    }
    if extension in JUNK_EXT:
        return False

    if filename.startswith('.env'):
        return False

    if any(keyword in filename.lower() for keyword in ['readme','architecture','contributing']):
        return size_in_bytes < 2_000_000

    if extension in ['.yaml','.yml','.toml','.json']:
        return size_in_bytes < 500_000

    return size_in_bytes < 300_000
