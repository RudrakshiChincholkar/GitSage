from llm.groq_client import generate_answer
from ingestion.repo_fetcher import normalize_repo_url

from vectorstore.chroma_store import ChromaStore
from repo_ingestion.unified_pipeline import _get_repo_version


# ---------------------------------------------------------
# Question Mode Detection
# ---------------------------------------------------------
def detect_question_mode(question: str) -> str:
    q = question.lower()

    if any(k in q for k in ["which files", "what files", "which file", "what file"]):
        return "INVENTORY"

    if any(k in q for k in [
        "what data", "which data",
        "what algorithm", "which algorithm",
        "what feature", "which feature",
        "implemented"
    ]):
        return "INVENTORY"

    if any(k in q for k in [
        "structure", "structured",
        "organization", "organized",
        "layout", "folders", "directory"
    ]):
        return "STRUCTURE"

    return "EXPLANATION"


# ---------------------------------------------------------
# Repo-level intent detection (IMPORTANT)
# ---------------------------------------------------------
def is_repo_intent_question(question: str) -> bool:
    q = question.lower()
    return any(k in q for k in [
        "what is this repository",
        "purpose of this repository",
        "about this repository",
        "what does this repo do",
        "main purpose of this repository",
        "why was this repository created"
    ])


# ---------------------------------------------------------
# Retrieval
# ---------------------------------------------------------
def search_repo(question: str, repo_url: str, k: int = 12):
    try:
        from repo_ingestion.unified_pipeline import get_retriever

        retriever = get_retriever()
        print(
            f"[qa_engine.search_repo] calling retriever.retrieve "
            f"repo_url={repo_url!r} query={question!r} top_k={k}"
        )

        raw = retriever.retrieve(query=question, top_k=k, repo_url=repo_url)

        print(f"[qa_engine.search_repo] retriever returned {len(raw)} results")
        for i, item in enumerate(raw[:5], 1):
            print(f"  {i}. {item.get('metadata')}")

        return [(item.get("document", ""), item.get("metadata", {})) for item in raw]

    except Exception as e:
        print("[qa_engine.search_repo] retrieval failed:", repr(e))
        return []

def ensure_repo_is_ready(repo_url: str) -> None:
    store = ChromaStore()
    repo_version = _get_repo_version(repo_url)

    if not repo_version:
        raise RuntimeError("Unable to determine repository version.")

    if not store.is_repo_ingested(repo_url, repo_version):
        raise RuntimeError(
            "Repository is still being ingested. Please wait for ingestion to complete."
        )

# ---------------------------------------------------------
# Main Q&A Entry Point
# ---------------------------------------------------------
def answer_question(repo_url: str, question: str):
    repo_url = normalize_repo_url(repo_url)

    ensure_repo_is_ready(repo_url)
    
    mode = detect_question_mode(question)

    # 🔑 Repo-intent questions should retrieve FEWER but STRONGER chunks
    if is_repo_intent_question(question):
        retrieved = search_repo(question, repo_url, k=6)
    else:
        retrieved = search_repo(question, repo_url, k=12)

    # -----------------------------------------------------
    # DEBUG (keep during development)
    # -----------------------------------------------------
    print("\nQuestion mode:", mode)
    print("Retrieved chunks:")
    for doc, meta in retrieved:
        print("-----")
        print(meta.get("path", "unknown"))
        print(doc[:200])

    # -----------------------------------------------------
    # STRUCTURE / INVENTORY → deterministic (NO LLM)
    # -----------------------------------------------------
    if mode in {"STRUCTURE", "INVENTORY"}:
        paths = []
        languages = set()
        types = set()

        for _, meta in retrieved:
            p = meta.get("path")
            if p:
                paths.append(p)

            lang = meta.get("language")
            if lang:
                languages.add(lang)

            t = meta.get("type")
            if t:
                types.add(t)

        unique_paths = sorted(set(paths))

        if mode == "STRUCTURE":
            dirs = sorted({"/".join(p.split("/")[:-1]) or "./" for p in unique_paths})

            out = ["Repository Structure (from indexed files):"]
            out.append("\nDirectories:")
            for d in dirs:
                out.append(f"- {d}")

            out.append("\nFiles:")
            for p in unique_paths:
                out.append(f"- {p}")

            if languages:
                out.append("\nLanguages:")
                for l in sorted(languages):
                    out.append(f"- {l}")

            return "\n".join(out)

        if mode == "INVENTORY":
            out = ["Inventory of explicit artifacts found:"]
            if unique_paths:
                out.append("\nFiles:")
                for p in unique_paths:
                    out.append(f"- {p}")

            if types:
                out.append("\nTypes:")
                for t in sorted(types):
                    out.append(f"- {t}")

            if languages:
                out.append("\nLanguages:")
                for l in sorted(languages):
                    out.append(f"- {l}")

            if len(out) == 1:
                return "No explicit inventory items found."

            return "\n".join(out)

    # -----------------------------------------------------
    # EXPLANATION → build LLM context
    # -----------------------------------------------------
    context_blocks = []

    # 🔑 Repo summary FIRST if present
    for doc, meta in retrieved:
        if meta.get("type") == "repo_summary":
            context_blocks.append("[REPOSITORY SUMMARY]\n" + doc)

    # 🔑 Then file-level chunks
    for doc, meta in retrieved:
        if meta.get("type") != "repo_summary":
            path = meta.get("path", "unknown")
            context_blocks.append(f"[FILE: {path}]\n{doc}")

    context = "\n\n".join(context_blocks)

    # -----------------------------------------------------
    # LLM Prompt
    # -----------------------------------------------------
    prompt = f"""
You are an expert assistant answering questions about a code repository.

Rules:
- Use ONLY the repository context provided.
- Ground all claims in the context.
- Do NOT hallucinate missing information.
- If the repository does not contain enough information, say so clearly.

Repository Context:
{context}

Question:
{question}

Answer clearly and concisely.
"""

    return generate_answer(prompt, question)

 