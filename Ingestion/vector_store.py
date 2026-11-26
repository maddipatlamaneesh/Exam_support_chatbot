import chromadb
import re

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

DB_DIR = BASE_DIR / "ChromaDB" / "My_Database"


client = chromadb.PersistentClient(
    path=str(DB_DIR)
)


# Create or retrieve collection
def create_collection(pdf_name):

    collection_name = Path(pdf_name).stem.lower()

    # Replace invalid characters
    collection_name = re.sub(
        r"[^a-z0-9_-]",
        "_",
        collection_name
    )

    # Ensure valid collection name length
    if len(collection_name) < 3:
        collection_name = collection_name + "_pdf"

    collection_name = collection_name[:63]

    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=None
    )

    return collection


# Prepare chunk records
def prepare_chunks(chunks):

    ids = []
    documents = []
    metadatas = []

    for i, chunk in enumerate(chunks):

        ids.append(f"chunk_{i + 1}")

        documents.append(chunk.page_content)

        metadata = chunk.metadata.copy()

        metadata["chunk_number"] = i + 1

        metadatas.append(metadata)

    return ids, documents, metadatas


# Clear existing collection records
def clear_collection(collection):

    existing_records = collection.get()

    if existing_records["ids"]:

        collection.delete(
            ids=existing_records["ids"]
        )


# Store records in ChromaDB
def store_chunks(
    collection,
    ids,
    documents,
    metadatas,
    embeddings
):

    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings.tolist()
    )