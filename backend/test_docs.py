# test_docs.py
from docs.doc_generator import generate_documentation
from repo_ingestion.unified_pipeline import get_retriever

repo_url = "https://github.com/RudrakshiChincholkar/GitSage"
retriever = get_retriever()

docs = generate_documentation(repo_url, retriever)
print("Generated sections:", list(docs.keys()))