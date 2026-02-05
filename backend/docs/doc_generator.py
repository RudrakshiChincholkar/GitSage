from llm.groq_client import generate_answer
from ingestion.repo_summary import get_repo_summary
from pprint import pprint


def generate_documentation(repo_url, retriever):
    """
    Generate comprehensive documentation for a repository.
    
    Args:
        repo_url: Repository URL
        retriever: Retriever instance to query ChromaDB
    
    Returns:
        dict: Documentation sections
    """
    
    print("\n" + "=" * 60)
    print("GENERATING REPOSITORY DOCUMENTATION")
    print("=" * 60)
    
    # Get repository summary
    repo_summary = get_repo_summary(repo_url)
    
    documentation = {}
    
    # ========================================
    # SECTION 1: OVERVIEW
    # ========================================
    print("\n[1/6] Generating Overview...")
    
    overview_queries = [
        "What is the main purpose of this repository?",
        "What does this project do?"
    ]
    
    # Retrieve context for overview
    overview_chunks = []
    for query in overview_queries:
        chunks = retriever.retrieve(query, top_k=3, repo_url=repo_url)
        print(f"[DOC_GEN] Retrieved {len(chunks)} chunks for query: {query}")
        if chunks:
            print("[DOC_GEN] Sample metadata:")
            pprint([c.get("metadata") for c in chunks[:2]])
            print("[DOC_GEN] Full chunk details:")
            for i, c in enumerate(chunks[:2]):
                print(f"  Chunk {i}:")
                print(f"    Keys: {c.keys()}")
                print(f"    Metadata: {c.get('metadata')}")
                doc = c.get("document")
                if isinstance(doc, list):
                    print(f"    Document is list with {len(doc)} items")
                    for j, d in enumerate(doc[:1]):
                        print(f"      Item {j}: length={len(d)}, preview={d[:100]!r}")
                else:
                    doc_len = len(doc or "")
                    doc_preview = (doc or "")[:100]
                    print(f"    Document: length={doc_len}, preview={doc_preview!r}")
        overview_chunks.extend(chunks)
    
    # Remove duplicates based on document content
    seen = set()
    unique_overview_chunks = []
    for chunk in overview_chunks:
        doc_str = str(chunk["document"])
        if doc_str not in seen:
            seen.add(doc_str)
            unique_overview_chunks.append(chunk)
    print(f"[DOC_GEN] Unique overview chunks count: {len(unique_overview_chunks)}")
    if unique_overview_chunks:
        print("[DOC_GEN] Sample document lengths and preview:")
        for c in unique_overview_chunks[:2]:
            doc = c.get("document")
            if isinstance(doc, list):
                doc_preview = "\n".join(doc)[:200]
                doc_len = sum(len(d) for d in doc)
            else:
                doc_preview = (doc or "")[:200]
                doc_len = len(doc or "")
            print(f" - length={doc_len}, preview={doc_preview!r}")
    
    overview_prompt = """Based on the code and files provided, write a concise overview of this repository.
Include:
- What the project does
- Main purpose/goal
- Target users or use case

Keep it 2-3 paragraphs maximum."""
    
    documentation["overview"] = generate_answer(
        unique_overview_chunks[:2],
        overview_prompt,
        repo_summary
    )
    print("✓ Overview generated")
    
    # ========================================
    # SECTION 2: ARCHITECTURE
    # ========================================
    print("\n[2/6] Generating Architecture...")
    
    architecture_queries = [
        "How is the codebase structured?",
        "What are the main modules and components?",
        "What design patterns are used?"
    ]
    
    architecture_chunks = []
    for query in architecture_queries:
        chunks = retriever.retrieve(query, top_k=4, repo_url=repo_url)
        print(f"[DOC_GEN] Retrieved {len(chunks)} chunks for architecture query: {query}")
        architecture_chunks.extend(chunks)
    
    # Remove duplicates
    seen = set()
    unique_arch_chunks = []
    for chunk in architecture_chunks:
        doc_str = str(chunk["document"])
        if doc_str not in seen:
            seen.add(doc_str)
            unique_arch_chunks.append(chunk)
    
    architecture_prompt = """Describe the architecture and structure of this codebase.
Include:
- Main directories/modules and their purposes
- How components interact
- Design patterns or architectural style used
- Technology stack

Keep it clear and organized."""
    
    documentation["architecture"] = generate_answer(
        unique_arch_chunks[:2],
        architecture_prompt,
        repo_summary
    )
    print("✓ Architecture generated")
    
    # ========================================
    # SECTION 3: SETUP INSTRUCTIONS
    # ========================================
    print("\n[3/6] Generating Setup Instructions...")
    
    setup_queries = [
        "How do I set up this project?",
        "What are the installation steps?",
        "How do I run this project?"
    ]
    
    setup_chunks = []
    for query in setup_queries:
        chunks = retriever.retrieve(query, top_k=3, repo_url=repo_url)
        setup_chunks.extend(chunks)
    
    # Remove duplicates
    seen = set()
    unique_setup_chunks = []
    for chunk in setup_chunks:
        doc_str = str(chunk["document"])
        if doc_str not in seen:
            seen.add(doc_str)
            unique_setup_chunks.append(chunk)
    
    setup_prompt = """Write clear setup and installation instructions for this project.
Include:
- Prerequisites (languages, tools, dependencies)
- Installation steps
- How to run the project
- Any configuration needed

Format as a numbered step-by-step guide."""
    
    documentation["setup"] = generate_answer(
        unique_setup_chunks[:2],
        setup_prompt,
        repo_summary
    )
    print("✓ Setup instructions generated")
    
    # ========================================
    # SECTION 4: KEY FEATURES
    # ========================================
    print("\n[4/6] Generating Key Features...")
    
    features_queries = [
        "What are the main features of this project?",
        "What functionality does this provide?"
    ]
    
    features_chunks = []
    for query in features_queries:
        chunks = retriever.retrieve(query, top_k=4, repo_url=repo_url)
        features_chunks.extend(chunks)
    
    # Remove duplicates
    seen = set()
    unique_features_chunks = []
    for chunk in features_chunks:
        doc_str = str(chunk["document"])
        if doc_str not in seen:
            seen.add(doc_str)
            unique_features_chunks.append(chunk)
    
    features_prompt = """List and describe the main features and functionality of this project.
Be specific about what users can do with this software.
Format as bullet points or numbered list."""
    
    documentation["features"] = generate_answer(
        unique_features_chunks[:2],
        features_prompt,
        repo_summary
    )
    print("✓ Key features generated")
    
    # ========================================
    # SECTION 5: DEPENDENCIES
    # ========================================
    print("\n[5/6] Generating Dependencies...")
    
    # Dependencies come from repo summary
    if repo_summary:
        deps_prompt = f"""Based on the repository summary and code, describe the main dependencies and libraries used.

Repository Summary:
{repo_summary}

Explain what each major dependency is used for."""
        
        documentation["dependencies"] = generate_answer(
            [],  # No chunks needed, using summary
            deps_prompt,
            repo_summary
        )
    else:
        documentation["dependencies"] = "No dependency information available."
    
    print("✓ Dependencies generated")
    
    # ========================================
    # SECTION 6: API/CODE REFERENCE
    # ========================================
    print("\n[6/6] Generating API Reference...")
    
    api_queries = [
        "What are the main functions and classes?",
        "What are the key API endpoints or methods?"
    ]
    
    api_chunks = []
    for query in api_queries:
        chunks = retriever.retrieve(query, top_k=5, repo_url=repo_url)
        api_chunks.extend(chunks)
    
    # Remove duplicates
    seen = set()
    unique_api_chunks = []
    for chunk in api_chunks:
        doc_str = str(chunk["document"])
        if doc_str not in seen:
            seen.add(doc_str)
            unique_api_chunks.append(chunk)
    
    api_prompt = """Document the main functions, classes, or API endpoints in this codebase.
Include:
- Function/class names
- What they do
- Key parameters or inputs
- Return values or outputs

Focus on the most important components."""
    
    documentation["api_reference"] = generate_answer(
        unique_api_chunks[:2],
        api_prompt,
        repo_summary
    )
    print("✓ API reference generated")
    
    print("\n" + "=" * 60)
    print("DOCUMENTATION GENERATION COMPLETE")
    print("=" * 60)
    
    return documentation


def format_documentation_markdown(documentation):
    """
    Format documentation dict as a plain text string without Markdown.
    
    Args:
        documentation: Dict with documentation sections
    
    Returns:
        str: Formatted markdown documentation
    """
    
    markdown = []
    
    markdown.append("# Repository Documentation\n")
    
    if "overview" in documentation:
        markdown.append("## Overview\n")
        markdown.append(documentation["overview"])
        markdown.append("\n")
    
    if "architecture" in documentation:
        markdown.append("## Architecture\n")
        markdown.append(documentation["architecture"])
        markdown.append("\n")
    
    if "setup" in documentation:
        markdown.append("## Getting Started\n")
        markdown.append(documentation["setup"])
        markdown.append("\n")
    
    if "features" in documentation:
        markdown.append("## Key Features\n")
        markdown.append(documentation["features"])
        markdown.append("\n")
    
    if "dependencies" in documentation:
        markdown.append("## Dependencies\n")
        markdown.append(documentation["dependencies"])
        markdown.append("\n")
    
    if "api_reference" in documentation:
        markdown.append("## API Reference\n")
        markdown.append(documentation["api_reference"])
        markdown.append("\n")
    
    markdown.append("---\n")
    markdown.append("*Documentation generated automatically by GitSage*\n")
    
    return "\n".join(markdown)
