from vectorstore.chroma_client import collection
from llm.groq_client import generate_answer
from ingestion.repo_fetcher import normalize_repo_url
from ingestion.repo_summary import get_repo_summary  # ADDED


def search_repo(question: str, repo_url: str, k: int = 15):
    # 🔎 Broader, implementation-focused query
    search_query = f"""
{question}

Look for actual code implementations, examples, logic, and data structures.
"""

    results = collection.query(
        query_texts=[search_query],
        n_results=k,
        where={"repo_url": repo_url}
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    # 🧠 Prefer CODE chunks
    code_chunks = [
        doc for doc, meta in zip(documents, metadatas)
        if meta.get("file_type") == "code"
    ]

    # Return top code chunks, fallback to docs
    return code_chunks[:5] if code_chunks else documents[:5]


def answer_question(repo_url: str, question: str):
    repo_url = normalize_repo_url(repo_url)
    chunks = search_repo(question, repo_url)

    summary = get_repo_summary(repo_url)  # ADDED

    # 🔎 DEBUG (keep during development)
    print("\nRetrieved chunks:")
    for c in chunks:
        print("-----")
        print(c[:300])

    context = "\n".join(chunks)
    if summary:  # ADDED
        # Prepend summary so high-level questions have structured metadata,  # ADDED
        # while preserving the original retrieved context.  # ADDED
        context = f"{summary}\n\n{context}"  # ADDED

    prompt = f"""
You are an expert code assistant.

Answer the user's question using ONLY the repository context below.
If something is not implemented, clearly say so.

Repository Context:
{context}

Question:
{question}

Answer clearly and concisely.
"""

    return generate_answer(prompt, question)
