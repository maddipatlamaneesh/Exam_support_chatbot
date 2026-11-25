from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


def chunk_documents(documents):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=120,
        separators=["\n\n", "\n", " ", ""]
    )

    input_documents = []

    for doc in documents:

        input_documents.append(
            Document(
                page_content=doc["text"],
                metadata=doc["metadata"]
            )
        )

    chunks = splitter.split_documents(input_documents)

    print("\n========== CHUNKING SUMMARY ==========")
    print("Input pages:", len(documents))
    print("Total chunks created:", len(chunks))

    return chunks


if __name__ == "__main__":

    from Ingestion.loader import load_pdf

    documents = load_pdf("AI_Part1_Theory_Quick_Revision.pdf")
    chunks = chunk_documents(documents)
    print(len(chunks))

    if chunks:
        print("\nFirst chunk:")
        print(chunks[0].page_content)

        print("\nFirst chunk metadata:")
        print(chunks[0].metadata)
