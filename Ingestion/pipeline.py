from Ingestion.loader import load_pdf, resolve_pdf_path
from Ingestion.chunker import chunk_documents
from Ingestion.embedder import generate_embeddings

from Ingestion.vector_store import (
    create_collection,
    clear_collection,
    get_file_hash,
    prepare_chunks,
    store_chunks
)


def ingest_pdf(pdf_path, source_name=None, return_details=False):
    """Ingest one PDF into its own persistent ChromaDB collection.

    The original string-only return value is retained by default for the CLI.
    Pass ``return_details=True`` when a caller needs upload status for a UI.
    """
    resolved_path = resolve_pdf_path(pdf_path)
    display_name = source_name or resolved_path.name
    document_hash = get_file_hash(resolved_path)

    # Step 1: Load PDF
    documents = load_pdf(resolved_path, source_name=display_name)

    # Step 2: Create chunks
    chunks = chunk_documents(documents)

    if not chunks:
        raise ValueError(f"No chunks could be created from PDF: {display_name}")

    # Step 3: Prepare records
    ids, texts, metadatas = prepare_chunks(chunks, document_hash=document_hash)

    # Step 4: Generate embeddings
    embeddings = generate_embeddings(texts)

    # Step 5: Create a collection that is unique to this file's content.
    collection = create_collection(display_name, document_hash=document_hash)
    replaced_existing = collection.count() > 0

    # Re-uploading the same file replaces old chunks rather than leaving stale
    # chunks alongside the new ingestion result.
    clear_collection(collection)

    # Step 6: Store chunks
    store_chunks(
        collection,
        ids,
        texts,
        metadatas,
        embeddings
    )

    if return_details:
        return {
            "collection_name": collection.name,
            "source_filename": display_name,
            "chunk_count": len(texts),
            "document_hash": document_hash,
            "replaced_existing": replaced_existing
        }

    # Preserve the original return value used by main.py.
    return collection.name
