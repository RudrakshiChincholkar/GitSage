# test_qa.py
from repo_ingestion.unified_pipeline import ingest_repository, get_retriever

# Step 1: Ingest the repository (if not already done)
print("=" * 60)
print("STEP 1: Ingesting Repository")
print("=" * 60)
repo_url = "https://github.com/RudrakshiChincholkar/GitSage"
ingest_result = ingest_repository(repo_url)
print(f"\nIngestion Result: {ingest_result}")

# Step 2: Retrieve results
print("\n" + "=" * 60)
print("STEP 2: Running Q&A Retrieval")
print("=" * 60)
retriever = get_retriever()
results = retriever.retrieve(
    "What does this repository do?",
    top_k=5,
    repo_url=repo_url
)

print(f"\nFound {len(results)} results:\n")
for i, result in enumerate(results, 1):
    print(f"\n{i}. Similarity: {result['similarity']:.4f}")
    print(f"   Source: {result['source']}")
    print(f"   File: {result['metadata'].get('path', 'N/A')}")
    print(f"   Preview: {result['document'][:200]}...")