import chromadb
from chromadb.config import Settings

# Persistent DB (saved on disk)
client = chromadb.Client(
    Settings(persist_directory="./chroma_db")
)

# Create / get collection
collection = client.get_or_create_collection(
    name="gitsage_repos"
)


def store_embeddings(documents, embeddings, metadatas, ids):
    collection.add(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )
