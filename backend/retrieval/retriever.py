from vectorstore.chroma_client import collection
from embeddings.embedder import embed_texts
from ingestion.repo_fetcher import normalize_repo_url


class Retriever:
    """
    Retriever class for documentation generation.
    Performs retrieval from ChromaDB.
    """
    
    def __init__(self):
        """Initialize retriever."""
        pass
    
    def retrieve(self, query: str, top_k: int = 5, repo_url: str = None):
        """
        Retrieve relevant chunks for a query.
        
        Args:
            query: Search query
            top_k: Number of results to return
            repo_url: Repository URL to filter by (optional)
        
        Returns:
            List of dicts with 'document', 'metadata', 'similarity'
        """
        print(f"\n[RETRIEVER] Query: {query}")
        print(f"[RETRIEVER] Top K: {top_k}")
        print(f"[RETRIEVER] Repo URL: {repo_url}")
        
        # Normalize repo URL if provided
        if repo_url:
            repo_url = normalize_repo_url(repo_url)
            print(f"[RETRIEVER] Normalized Repo URL: {repo_url}")
        
        # Embed the query as text
        query_embedding = embed_texts([query])[0]
        print(f"[RETRIEVER] Query embedding generated (length: {len(query_embedding)})")
        
        # Build query parameters
        query_params = {
            "query_embeddings": [query_embedding],
            "n_results": top_k,
            "include": ["documents", "metadatas", "distances"]
        }
        
        # Add repository filter if provided
        if repo_url:
            query_params["where"] = {"repo_url": repo_url}
            print(f"[RETRIEVER] Filtering by repo_url: {repo_url}")
        
        # Query ChromaDB
        try:
            results = collection.query(**query_params)
            print(f"[RETRIEVER] ChromaDB query successful")
            
            # Debug: Print what we got back
            if results and results.get("documents"):
                print(f"[RETRIEVER] Found {len(results['documents'][0])} results")
            else:
                print("[RETRIEVER] WARNING: No results returned from ChromaDB")
                
        except Exception as e:
            print(f"[RETRIEVER] ERROR querying ChromaDB: {e}")
            return []
        
        # Format results
        formatted_results = []
        
        if results and results.get("documents") and len(results["documents"]) > 0:
            documents = results["documents"][0]
            metadatas = results["metadatas"][0]
            distances = results["distances"][0]
            
            for i, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances)):
                print(f"[RETRIEVER] Result {i+1}: {meta.get('file_path', 'unknown')} (distance: {dist:.4f})")
                formatted_results.append({
                    "document": doc,
                    "metadata": meta,
                    "similarity": 1 - dist  # Convert distance to similarity
                })
        else:
            print("[RETRIEVER] WARNING: No documents in results")
        
        print(f"[RETRIEVER] Returning {len(formatted_results)} formatted results\n")
        return formatted_results