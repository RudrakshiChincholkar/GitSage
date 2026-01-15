from vectorstore.chroma_client import collection
from llm.groq_client import generate_answer


def search_repo(question: str, repo_url: str, k: int = 5):
    results = collection.query(
        query_texts=[question],
        n_results=k,
        where={"repo_url": repo_url}
    )

    return results.get("documents", [[]])[0]


def answer_question(question: str, repo_url: str):
    chunks = search_repo(question, repo_url)

    context = "\n".join(chunks)

    prompt = f"""
Answer the question using ONLY the context below.

Context:
{context}

Question:
{question}
"""

    return generate_answer(prompt)
