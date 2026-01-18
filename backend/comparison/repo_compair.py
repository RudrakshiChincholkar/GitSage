from typing import List
from vectorstore.chroma_client import collection
from llm.groq_client import generate_answer


def search_repo_for_feature(question: str, repo_url: str, k: int = 4):
    """Search for relevant chunks for a specific question in a repository."""
    results = collection.query(
        query_texts=[question],
        n_results=k,
        where={"repo_url": repo_url}
    )
    return results.get("documents", [[]])[0]


def repo_exists_in_db(repo_url: str) -> bool:
    """Check if a repository has embeddings stored in the database."""
    results = collection.get(
        where={"repo_url": repo_url},
        limit=1
    )
    return len(results.get("ids", [])) > 0


def compare_repositories(question: str, repo_urls: List[str]):
    """
    Compare two or more repositories based on a question.
    
    Args:
        question: The comparison question/query
        repo_urls: List of repository URLs to compare (length >= 2)
    
    Returns:
        Comparison answer string from the LLM
    
    Raises:
        ValueError: If less than 2 repos provided or if any repo not found in database
    """
    if len(repo_urls) < 2:
        raise ValueError("At least 2 repository URLs are required for comparison")
    
    # Check if all repositories exist in the database
    missing_repos = []
    for repo_url in repo_urls:
        if not repo_exists_in_db(repo_url):
            missing_repos.append(repo_url)
    
    if missing_repos:
        if len(missing_repos) == 1:
            raise ValueError(
                f"Repository not found in database: {missing_repos[0]}. "
                f"Please ingest it first using /ingest-repo endpoint."
            )
        else:
            repos_list = ", ".join(missing_repos)
            raise ValueError(
                f"Repositories not found in database: {repos_list}. "
                f"Please ingest them first using /ingest-repo endpoint."
            )
    
    feature_queries = {
        "purpose": "what is the purpose of this repository?",
        "functionality": "what are the main features and functionality?",
        "architecture": "how is the code structured or architected?",
        "tech": "what technologies and frameworks are used?",
        "complexity": "how complex is the codebase?",
        "ui": "does the repository include a UI or user interface?"
    }
    
    # Collect context for each repository and feature
    repo_contexts = {}
    for repo_url in repo_urls:
        repo_contexts[repo_url] = {}
    
    # Query each repository for each feature
    for feature, query_text in feature_queries.items():
        for repo_url in repo_urls:
            chunks = search_repo_for_feature(query_text, repo_url, k=4)
            repo_contexts[repo_url][feature] = chunks
    
    # Build structured prompt (generalized for N repositories)
    repo_sections = []
    for idx, repo_url in enumerate(repo_urls, start=1):
        repo_label = chr(64 + idx)  # A, B, C, ...
        
        repo_context = repo_contexts[repo_url]
        
        section = f"""
====================
REPOSITORY {repo_label}
====================

Purpose:
{"\n".join(repo_context["purpose"])}

Functionality:
{"\n".join(repo_context["functionality"])}

Architecture / Code Structure:
{"\n".join(repo_context["architecture"])}

Technology Stack:
{"\n".join(repo_context["tech"])}

Complexity:
{"\n".join(repo_context["complexity"])}

UI / Interface:
{"\n".join(repo_context["ui"])}
"""
        repo_sections.append(section)
    
    # Build comparison task section
    comparison_section = " vs ".join([chr(64 + i) for i in range(1, len(repo_urls) + 1)])
    
    # Build feature comparison lines for output format
    feature_comparison_lines = []
    for feature in feature_queries.keys():
        feature_display = {
            "purpose": "Purpose",
            "functionality": "Functionality",
            "architecture": "Architecture / Code Structure",
            "tech": "Technology Stack",
            "complexity": "Complexity",
            "ui": "UI / Interface"
        }[feature]
        
        feature_comparison_lines.append(f"\n{feature_display} Comparison:")
        for idx, repo_url in enumerate(repo_urls, start=1):
            repo_label = chr(64 + idx)
            feature_comparison_lines.append(f"- Repository {repo_label}:")
    
    prompt = f"""
You are a senior software engineer performing a repository comparison.

You are given extracted evidence for {len(repo_urls)} GitHub repositories.
Use ONLY the provided information.
Do NOT guess or hallucinate.

{''.join(repo_sections)}

====================
TASK
====================

Compare the repositories ({comparison_section}) for EACH feature below.

Rules:
- Always contrast the repositories against each other
- Use at most 2 bullet points per repository per feature
- Each bullet must be ONE sentence
- If a feature is missing, write "Not specified"
- Do NOT repeat phrases
- Do NOT copy raw text from the context

====================
OUTPUT FORMAT (STRICT)
====================
{''.join(feature_comparison_lines)}

Final Comparison Summary:
"""
    
    return generate_answer(prompt)
