import os
import uuid
import chromadb
from chromadb.config import Settings

# Get absolute path for persistent DB
base_dir = os.path.dirname(os.path.abspath(__file__))
persist_dir = os.path.join(base_dir, "chroma_db")

print(f"[chroma_client] Using persist_directory={persist_dir}")

# Use PersistentClient for actual persistence to disk
client = chromadb.PersistentClient(
    path=persist_dir
)

# Create / get collection
collection = client.get_or_create_collection(
    name="gitsage_repos"
)


def store_embeddings(
    documents: list[str],
    embeddings: list[list[float]],
    metadatas: list[dict]
):
    """
    Store chunks + embeddings safely into Chroma.
    IDs are generated internally to avoid collisions.
    """

    if not documents:
        return

    assert len(documents) == len(embeddings) == len(metadatas)

    ids = [str(uuid.uuid4()) for _ in documents]

    collection.add(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )


def similarity_search(
    query_embedding: list[float],
    k: int = 5
):
    """
    Retrieve top-k relevant chunks.
    """
    return collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["documents", "metadatas", "distances"]
    )
