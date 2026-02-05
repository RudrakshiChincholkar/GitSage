from llm.groq_client import generate_answer
from ingestion.repo_fetcher import normalize_repo_url
from ingestion.repo_summary import get_repo_summary


# ---------------------------------------------------------
# Question Mode Detection (GENERIC & LIGHTWEIGHT)
# ---------------------------------------------------------
def detect_question_mode(question: str) -> str:
    q = question.lower()

    # Questions asking for specific files should be treated as an inventory request
    if any(k in q for k in ["which files", "what files", "which file", "what file"]):
        return "INVENTORY"

    # Inventory-style questions (strict listing)
    if any(k in q for k in [
        "what data", "which data",
        "what algorithm", "which algorithm",
        "what feature", "which feature",
        "implemented"
    ]):
        return "INVENTORY"

    # Structure / organization questions
    if any(k in q for k in [
        "structure", "structured",
        "organization", "organized",
        "layout", "folders", "directory"
    ]):
        return "STRUCTURE"

    # Everything else → explanation / how / why
    return "EXPLANATION"


# ---------------------------------------------------------
# Retrieval (UNCHANGED BEHAVIOR)
# ---------------------------------------------------------
def search_repo(question: str, repo_url: str, k: int = 12):
    # Use the Retriever abstraction (dual embeddings + chroma store)
    try:
        from repo_ingestion.unified_pipeline import get_retriever
        retriever = get_retriever()
        print(f"[qa_engine.search_repo] calling retriever.retrieve with repo_url={repo_url!r} query={question!r} top_k={k}")
        raw = retriever.retrieve(query=question, top_k=k, repo_url=repo_url)
        print(f"[qa_engine.search_repo] retriever returned {len(raw)} raw results")
        # Dump first few metadatas for debugging
        for i, item in enumerate(raw[:6], 1):
            try:
                print(f"  raw[{i}] metadata: {item.get('metadata')}")
            except Exception:
                print(f"  raw[{i}] metadata: <unavailable>")

        # raw is a list of dicts with keys: similarity, document, metadata, source
        pairs = [(item.get('document', ''), item.get('metadata', {})) for item in raw]
        return pairs
    except Exception as e:
        print("[qa_engine.search_repo] fallback direct chroma query failed:", repr(e))
        return []


# ---------------------------------------------------------
# Main Q&A Entry Point
# ---------------------------------------------------------
def answer_question(repo_url: str, question: str):
    repo_url = normalize_repo_url(repo_url)

    mode = detect_question_mode(question)
    retrieved = search_repo(question, repo_url)
    summary = get_repo_summary(repo_url)

    # Debug (keep while developing)
    print("\nQuestion mode:", mode)
    print("Retrieved chunks:")
    for doc, meta in retrieved:
        print("-----")
        print(meta.get("file_path", "unknown"))
        print(doc[:300])

    # -----------------------------------------------------
    # Build context (STRUCTURAL + SEMANTIC)
    # -----------------------------------------------------
    context_blocks = []

    # Structural summary helps STRUCTURE + INVENTORY questions
    if summary and mode in {"STRUCTURE", "INVENTORY"}:
        context_blocks.append("[REPOSITORY SUMMARY]\n" + summary)

    # Semantic chunks (always included)
    for doc, meta in retrieved:
        path = meta.get("file_path", "unknown")
        context_blocks.append(f"[FILE: {path}]\n{doc}")

    context = "\n\n".join(context_blocks)

    # -----------------------------------------------------
    # Mode-specific prompts (THIS IS THE FIX)
    # -----------------------------------------------------

    INVENTORY_RULES = """
Answer rules for this question:
- List ONLY items that are explicitly implemented in the repository.
- Do NOT include items that are only implied by usage.
- Do NOT include standard library containers.
- Do NOT include helper or internal components.
- If an item exists only as part of another structure, do NOT list it separately.
- If nothing qualifies, clearly say so.
"""

    STRUCTURE_RULES = """
Answer rules for this question:
- Report ONLY what is directly observable from the repository structure.
- List directories, files, and programming languages present.
- Do NOT describe purpose, intent, or usage of any directory or file.
- Do NOT infer meaning from names.
- Do NOT use speculative language (e.g., "might", "likely", "used for").
- If something is not explicitly stated in the repository, do not mention it.
"""

    EXPLANATION_RULES = """
Answer rules for this question:
- Explain using the provided repository context.
- You may reason about behavior, but ground claims in code or comments.
- If something is unclear or missing, say so explicitly.
"""

    if mode == "INVENTORY":
        rules = INVENTORY_RULES
    elif mode == "STRUCTURE":
        rules = STRUCTURE_RULES
    else:
        rules = EXPLANATION_RULES

    # -----------------------------------------------------
    # Final Prompt (GENERIC, REPO-AGNOSTIC)
    # -----------------------------------------------------
    # If the question is structural or inventory-style, answer deterministically
    if mode in {"STRUCTURE", "INVENTORY"}:
        # Collect metadata from retrieved chunks
        paths = []
        languages = set()
        file_types = set()
        for doc, meta in retrieved:
            p = meta.get("file_path") or meta.get("path") or "unknown"
            paths.append(p)
            lang = meta.get("language")
            if lang:
                languages.add(lang)
            ft = meta.get("file_type") or meta.get("type")
            if ft:
                file_types.add(ft)

        # Exclude unknown placeholders
        unique_paths = sorted({p for p in paths if p and p != "unknown"})

        if mode == "STRUCTURE":
            # Report directories and files observed
            dirs = sorted({"/".join(p.split("/")[:-1]) or "./" for p in unique_paths})
            parts = ["Repository Structure (observed from indexed files):"]
            parts.append("\nDirectories:")
            for d in dirs:
                parts.append(f"- {d}")
            parts.append("\nFiles:")
            for p in unique_paths:
                parts.append(f"- {p}")
            if languages:
                parts.append("\nLanguages observed:")
                for L in sorted(languages):
                    parts.append(f"- {L}")
            return "\n".join(parts)

        if mode == "INVENTORY":
            # For inventory, list implemented artifacts that are explicit in metadata
            parts = ["Inventory of explicit items found in repository:"]
            if unique_paths:
                parts.append("\nCode files:")
                for p in unique_paths:
                    parts.append(f"- {p}")
            if file_types:
                parts.append("\nTypes observed:")
                for ft in sorted(file_types):
                    parts.append(f"- {ft}")
            if languages:
                parts.append("\nLanguages observed:")
                for L in sorted(languages):
                    parts.append(f"- {L}")
            if len(parts) == 1:
                return "No explicit inventory items found in the retrieved repository context."
            return "\n".join(parts)

    # -----------------------------------------------------
    # Final Prompt (GENERIC, REPO-AGNOSTIC)
    # -----------------------------------------------------

    prompt = f"""
You are an expert assistant answering questions about a code repository.

{rules}

General guidelines:
- Use ONLY the repository context provided below.
- Cite file paths when relevant.
- Do NOT hallucinate missing information.
- If the repository does not contain the requested information, say so clearly.

Repository Context:
{context}

Question:
{question}

Answer clearly, accurately, and concisely.
"""

    return generate_answer(prompt, question)
