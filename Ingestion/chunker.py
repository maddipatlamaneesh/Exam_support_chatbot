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

    return chunks