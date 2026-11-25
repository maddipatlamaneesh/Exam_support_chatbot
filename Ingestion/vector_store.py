import chromadb
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

DB_DIR = BASE_DIR / "ChromaDB" / "My_Database"


client = chromadb.PersistentClient(
    path=str(DB_DIR)
)


def create_collection(pdf_name):

    collection_name = Path(pdf_name).stem.lower()

    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=None
    )

    print("Collection created:", collection_name)

    return collection


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

if __name__ == "__main__":

    from Ingestion.loader import load_pdf
    from Ingestion.chunker import chunk_documents
    from Ingestion.embedder import generate_embeddings

    pdf_name = "AI_Part1_Theory_Quick_Revision.pdf"

    # Step 1: Load PDF
    documents = load_pdf(pdf_name)

    # Step 2: Create chunks
    chunks = chunk_documents(documents)

    # Step 3: Create ChromaDB collection
    collection = create_collection(pdf_name)

    # Step 4: Prepare records
    ids, texts, metadatas = prepare_chunks(chunks)

    # Step 5: Generate embeddings
    embeddings = generate_embeddings(texts)

    # Step 6: Store records in ChromaDB
    collection.add(
        ids=ids,
        documents=texts,
        metadatas=metadatas,
        embeddings=embeddings.tolist()
    )

    # Step 7: Verify storage
    print("\n========== STORAGE SUMMARY ==========")
    print("Total records stored:", collection.count())