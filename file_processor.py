from file_cleaner import clean_file_content
from chunker import chunk_files

# function declarations (jaroori to clean before we chunk and embedd)

def is_binary(content):
    if not content:
        return True
    
    binary_chars = 0

    for c in content:
        if ord(c) < 9 or ord(c) > 126:
            binary_chars+=1

    ratio = binary_chars/ len(content)

    return ratio > 0.3  # if more than 30% is binary then its not useful for embedding


def is_minified(content):
    lines = content.splitlines()

    if len(lines) < 3 and len(content) > 1000:
        return True
    
    avg_line_len = sum(len(l) for l in lines ) / max(len(lines) , 1)

    return avg_line_len > 300 

def is_too_small(content):
    return len(content.strip()) < 50

def is_valid_text(content):
    try:
        content.encode("utf-8")
        return True
    except:
        return False

def validate_files(downloaded_files):

    processed_files = {}

    for path,content in  downloaded_files.items():
        if not is_valid_text(content):
            continue
        
        if is_binary(content):
            continue
        
        if is_minified(content):
            continue

        if is_too_small(content):
            continue
        

        cleaned = clean_file_content(content)
        
        if not cleaned:
            continue 
        processed_files[path] = cleaned

    return processed_files


from step1_pipeline import run_step1

def run_step2_validation(repo_link):
    downloaded_files = run_step1(repo_link)
    validated_files = validate_files(downloaded_files)
    chunks = chunk_files(validated_files)
    return chunks
