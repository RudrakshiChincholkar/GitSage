import re

def get_repo_details(url):
    pattern = r"github\.com[:/](?P<user>[^/]+)/(?P<repo>[^/.]+)"
    match = re.search(pattern , url)

    if match:
        return match.group("user"), match.group("repo")
        
    return None
 