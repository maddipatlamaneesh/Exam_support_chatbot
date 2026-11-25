import chromadb
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DB_DIR = BASE_DIR / "ChromaDB" / "My_Database"

client = chromadb.PersistentClient(
    path=str(DB_DIR)
)


# Create or retrieve collection
def create_collection(pdf_name):

    collection_name = Path(pdf_name).stem.lower()

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


# Store records in ChromaDB
def store_chunks(collection, ids, documents, metadatas, embeddings):

    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings.tolist()
    )