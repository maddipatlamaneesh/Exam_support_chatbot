import os

from Ingestion.loader import load_pdf
from Ingestion.chunker import chunk_documents
from Ingestion.embedder import generate_embeddings

from Ingestion.vector_store import (
    create_collection,
    prepare_chunks,
    store_chunks
)


def ingest_pdf(pdf_path):

    # Step 1: Load PDF
    documents = load_pdf(pdf_path)

    # Step 2: Create chunks
    chunks = chunk_documents(documents)

    # Step 3: Prepare records
    ids, texts, metadatas = prepare_chunks(chunks)

    # Step 4: Generate embeddings
    embeddings = generate_embeddings(texts)

    # Step 5: Get PDF filename
    pdf_name = os.path.basename(pdf_path)

    # Step 6: Create collection
    collection = create_collection(pdf_name)

    # Step 7: Store chunks
    store_chunks(
        collection,
        ids,
        texts,
        metadatas,
        embeddings
    )

    # Return collection name
    return collection.name