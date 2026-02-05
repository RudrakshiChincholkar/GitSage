# this file is for validating the downloaded files (its like double checking ) before we 
# move on and make chunks


from repo_ingestion.file_cleaner import clean_file_content
from repo_ingestion.chunker_new import chunk_files

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


#  in this function the dowloaded files are also cleaned(remove blank lines unnecessary new lines)
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


from repo_ingestion.step1_pipeline import run_step1

def run_step2_validation(downloaded_files):
    """
    Input: dict[path -> file_content]
    Output: list of validated + chunked objects
    """
    cleaned_files = validate_files(downloaded_files)
    chunks = chunk_files(cleaned_files)
    return chunks

