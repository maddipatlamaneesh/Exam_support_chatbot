import chromadb
import hashlib
import re

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

DB_DIR = BASE_DIR / "ChromaDB" / "My_Database"


client = chromadb.PersistentClient(
    path=str(DB_DIR)
)


def get_file_hash(pdf_path):
    """Calculate a stable identity for a file without loading it all into memory."""
    digest = hashlib.sha256()

    with Path(pdf_path).open("rb") as pdf_file:
        for block in iter(lambda: pdf_file.read(1024 * 1024), b""):
            digest.update(block)

    return digest.hexdigest()


def _get_collection_name(collection):
    return collection if isinstance(collection, str) else collection.name


def _sanitize_collection_stem(pdf_name):
    collection_stem = Path(pdf_name).stem.lower()

    collection_stem = re.sub(
        r"[^a-z0-9._-]",
        "_",
        collection_stem
    ).strip("._-")

    return collection_stem or "document"


def build_collection_name(pdf_name, document_hash=None):
    """Build a Chroma-safe collection name unique to the uploaded file content."""
    collection_stem = _sanitize_collection_stem(pdf_name)

    if not document_hash:
        # Keep CLI compatibility for callers that only provide a filename.
        if len(collection_stem) < 3:
            collection_stem = collection_stem + "_pdf"
        return collection_stem[:63].rstrip("._-")

    # A 40-character SHA-256 prefix leaves room for a readable filename and
    # prevents separate PDFs with the same filename from sharing a collection.
    hash_suffix = document_hash[:40]
    max_stem_length = 63 - len(hash_suffix) - 1
    collection_stem = collection_stem[:max_stem_length].rstrip("._-")

    return f"{collection_stem}_{hash_suffix}"


# Create or retrieve collection
def create_collection(pdf_name, document_hash=None):

    collection_name = build_collection_name(pdf_name, document_hash)
    collection_metadata = {
        "source_filename": Path(pdf_name).name
    }

    if document_hash:
        collection_metadata["document_hash"] = document_hash

    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=None,
        metadata=collection_metadata
    )

    # Older collections do not have metadata. Preserve it rather than
    # overwriting it, while ensuring a new collection is self-describing.
    if not collection.metadata:
        collection.modify(metadata=collection_metadata)

    return collection

# Prepare chunk records
def prepare_chunks(chunks, document_hash=None):

    ids = []
    documents = []
    metadatas = []

    for i, chunk in enumerate(chunks):

        ids.append(f"chunk_{i + 1}")

        documents.append(chunk.page_content)

        metadata = chunk.metadata.copy()

        metadata["chunk_number"] = i + 1

        if document_hash:
            metadata["document_hash"] = document_hash

        metadatas.append(metadata)

    return ids, documents, metadatas


# Clear existing collection records
def clear_collection(collection):

    existing_records = collection.get()

    if existing_records["ids"]:

        collection.delete(
            ids=existing_records["ids"]
        )


def list_document_collections():
    """List persisted documents using filenames suitable for the UI.

    Collections created before document metadata existed are supported by
    reading the source field from their first stored chunk.
    """
    documents = []

    for collection_ref in client.list_collections():
        collection_name = _get_collection_name(collection_ref)
        collection = client.get_collection(name=collection_name)
        metadata = collection.metadata or {}
        source_filename = metadata.get("source_filename")

        if not source_filename and collection.count():
            record = collection.get(limit=1, include=["metadatas"])
            record_metadatas = record.get("metadatas") or []

            if record_metadatas:
                source_filename = record_metadatas[0].get("source")

        documents.append({
            "collection_name": collection_name,
            "source_filename": source_filename or f"{collection_name}.pdf",
            "document_hash": metadata.get("document_hash"),
            "chunk_count": collection.count()
        })

    return sorted(
        documents,
        key=lambda document: (
            document["source_filename"].lower(),
            document["collection_name"]
        )
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
