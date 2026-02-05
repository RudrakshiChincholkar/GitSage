import os
import re
import uuid

# language detection
def detect_language(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    mapping = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".java": "java",
        ".cpp": "cpp",
        ".c": "c",
        ".h": "c",
        ".hpp": "cpp",
        ".go": "go",
        ".rs": "rust",
        ".md": "markdown",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".json": "json",
        ".toml": "toml",
        ".ini": "ini",
        ".env": "env"
    }

    return mapping.get(ext, "text")  # text is the fall back if no matching is found

# markdown chunking 

def chunk_markdown(content):
    lines = content.splitlines()

    current = []
    chunks = []

    for line in lines:
        if line.startswith("#"):
            if current:
                chunks.append(current)
                current = []
        
        current.append(line)

    if current:
        chunks.append("\n".join(current))

    return chunks

# python chunking
def chunk_python(content):
    pattern = re.compile(r"^(class|def)\s+", re.MULTILINE)
    matches = list(pattern.finditer(content))

    if not matches:
        return [content]

    chunks = []

    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        chunk = content[start:end].strip()
        if len(chunk) > 0:
            chunks.append(chunk)

    return chunks


# JS/TS chunking
def chunk_javascript(content):
    pattern = re.compile(r"(function\s+\w+|const\s+\w+\s*=\s*\(|class\s+\w+)", re.MULTILINE)
    matches = list(pattern.finditer(content))

    if not matches:
        return [content]

    chunks = []

    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        chunk = content[start:end].strip()
        if len(chunk) > 0:
            chunks.append(chunk)

    return chunks

# In chunker.py, add overlap to chunk_by_size
def chunk_by_size(content, max_chars=1500, overlap=150):
    chunks = []
    lines = content.splitlines()
    current = []
    size = 0
    
    for line in lines:
        size += len(line)
        current.append(line)
        
        if size >= max_chars:
            chunks.append("\n".join(current))
            # Keep last few lines for overlap
            overlap_lines = current[-(overlap//20):] if len(current) > 5 else current[-2:]
            current = overlap_lines
            size = sum(len(l) for l in current)
    
    if current:
        chunks.append("\n".join(current))
    
    return chunks

# actuall chunking
def determine_chunk_type(language, path):
    if language in ["markdown", "text"]:
        return "text"
    return "code"


def chunk_file(path, content):

    language = detect_language(path)

    if language == "markdown":
        raw_chunks = chunk_markdown(content)
    elif language == "python":
        raw_chunks = chunk_python(content)
    elif language in ["javascript", "typescript"]:
        raw_chunks = chunk_javascript(content)
    else:
        raw_chunks = chunk_by_size(content)

    chunk_objects = []

    for chunk in raw_chunks:
        chunk_objects.append({
            "id": str(uuid.uuid4()),
            "path": path,
            "language": language,
            "type": determine_chunk_type(language, path),
            "text": chunk,
            "size": len(chunk)
        })
    
    return chunk_objects

def chunk_files(cleaned_files):
    all_chunks = []

    for path,content  in cleaned_files.items():
        file_chunks = chunk_file(path,content)
        all_chunks.extend(file_chunks)
    return all_chunks