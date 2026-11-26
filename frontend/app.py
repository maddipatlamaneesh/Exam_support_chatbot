"""Streamlit interface for the multi-document AI Exam Support Chatbot."""

from collections import Counter
import hashlib
from pathlib import Path
import re
import sys

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
UPLOAD_DIR = PROJECT_ROOT / "DATA" / "uploads"

# `streamlit run frontend/app.py` places frontend/ on sys.path, so add the
# project root before importing the existing backend packages.
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Ingestion.vector_store import list_document_collections


def initialise_session_state():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "ingestion_results" not in st.session_state:
        st.session_state.ingestion_results = []


def validate_upload(uploaded_file):
    """Perform inexpensive validation before persisting an uploaded file."""
    display_name = Path(uploaded_file.name).name

    if not display_name.lower().endswith(".pdf"):
        raise ValueError(f"{display_name} is not a PDF file.")

    file_bytes = uploaded_file.getvalue()

    if not file_bytes:
        raise ValueError(f"{display_name} is empty.")

    if not file_bytes.lstrip().startswith(b"%PDF-"):
        raise ValueError(f"{display_name} does not contain a valid PDF header.")

    return display_name, file_bytes


def save_uploaded_pdf(uploaded_file):
    """Save an upload under its hash so equal filenames can never overwrite."""
    display_name, file_bytes = validate_upload(uploaded_file)
    document_hash = hashlib.sha256(file_bytes).hexdigest()
    safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", display_name)
    destination = UPLOAD_DIR / f"{document_hash}_{safe_name}"

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    if destination.exists():
        existing_hash = hashlib.sha256(destination.read_bytes()).hexdigest()

        if existing_hash != document_hash:
            raise RuntimeError(
                "An upload storage collision was detected. Please rename the file and try again."
            )
    else:
        destination.write_bytes(file_bytes)

    return destination, display_name


def document_labels(documents):
    """Create human-readable, unique labels while keeping collection IDs hidden."""
    filename_counts = Counter(
        document["source_filename"] for document in documents
    )
    labels = {}

    for document in documents:
        label = document["source_filename"]

        if filename_counts[label] > 1:
            identifier = (
                document["document_hash"][:8]
                if document["document_hash"]
                else document["collection_name"][-8:]
            )
            label = f"{label} ({identifier})"

        labels[label] = document

    return labels


def render_sources(sources):
    source_pages = []

    for source in sources:
        metadata = source["metadata"]
        source_page = (
            metadata.get("source", "Unknown source"),
            metadata.get("page", "Unknown page")
        )

        if source_page not in source_pages:
            source_pages.append(source_page)

    if source_pages:
        with st.expander("Sources used"):
            for source_name, page_number in source_pages:
                st.markdown(f"- `{source_name}`, page {page_number}")


def render_chat_history(collection_name):
    for message in st.session_state.chat_history:
        if message["collection_name"] != collection_name:
            continue

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message["role"] == "assistant":
                render_sources(message.get("sources", []))


def ingest_uploads(uploaded_files):
    progress = st.progress(0, text="Preparing uploaded PDFs...")
    results = []

    for index, uploaded_file in enumerate(uploaded_files, start=1):
        name = Path(uploaded_file.name).name
        progress.progress(
            (index - 1) / len(uploaded_files),
            text=f"Processing {name} ({index} of {len(uploaded_files)})..."
        )

        try:
            saved_path, display_name = save_uploaded_pdf(uploaded_file)
            details = ingest_document(
                saved_path,
                source_name=display_name
            )
            action = "Re-indexed" if details["replaced_existing"] else "Ingested"
            results.append({
                "level": "success",
                "message": (
                    f"{action} {display_name} "
                    f"({details['chunk_count']} chunks)."
                )
            })
        except Exception as error:
            results.append({
                "level": "error",
                "message": f"Could not ingest {name}: {error}"
            })

        progress.progress(index / len(uploaded_files))

    progress.empty()
    return results


def ingest_document(pdf_path, source_name):
    """Load the embedding model only when a user starts an ingestion job."""
    from Ingestion.pipeline import ingest_pdf

    return ingest_pdf(
        pdf_path,
        source_name=source_name,
        return_details=True
    )


def ask_question(question, document):
    """Import the Gemini client only when the user asks a question."""
    from Generator.generator import generate_answer

    return generate_answer(
        question,
        collection_name=document["collection_name"],
        include_sources=True
    )


def main():
    st.set_page_config(
        page_title="AI Exam Support Chatbot",
        page_icon="📚",
        layout="wide"
    )
    initialise_session_state()

    st.title("📚 AI Exam Support Chatbot")
    st.caption(
        "Upload course PDFs, select one document, and ask questions grounded only in that document."
    )

    for result in st.session_state.ingestion_results:
        getattr(st, result["level"])(result["message"])
    st.session_state.ingestion_results = []

    with st.sidebar:
        st.header("Add study material")
        uploaded_files = st.file_uploader(
            "Upload one or more PDFs",
            type=["pdf"],
            accept_multiple_files=True,
            help="Each PDF is stored and indexed in its own persistent collection."
        )

        if st.button(
            "Ingest uploaded PDFs",
            disabled=not uploaded_files,
            use_container_width=True
        ):
            st.session_state.ingestion_results = ingest_uploads(uploaded_files)
            st.rerun()

    documents = list_document_collections()

    if not documents:
        st.info("Upload at least one PDF from the sidebar to begin.")
        return

    labels = document_labels(documents)
    selected_label = st.selectbox(
        "Select Document",
        options=list(labels),
        help="Questions are searched only within the selected document."
    )
    selected_document = labels[selected_label]

    st.caption(
        f"{selected_document['chunk_count']} indexed chunks available for {selected_document['source_filename']}."
    )

    clear_chat, _ = st.columns([1, 4])
    with clear_chat:
        if st.button("Clear chat"):
            st.session_state.chat_history = [
                message
                for message in st.session_state.chat_history
                if message["collection_name"] != selected_document["collection_name"]
            ]
            st.rerun()

    render_chat_history(selected_document["collection_name"])

    question = st.chat_input(
        f"Ask a question about {selected_document['source_filename']}"
    )

    if not question:
        return

    user_message = {
        "role": "user",
        "content": question,
        "collection_name": selected_document["collection_name"]
    }
    st.session_state.chat_history.append(user_message)

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Searching the selected document and preparing an answer..."):
                response = ask_question(question, selected_document)

            st.markdown(response["answer"])
            render_sources(response["sources"])
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response["answer"],
                "sources": response["sources"],
                "collection_name": selected_document["collection_name"]
            })
        except Exception as error:
            message = f"Unable to generate an answer: {error}"
            st.error(message)
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": message,
                "sources": [],
                "collection_name": selected_document["collection_name"]
            })


if __name__ == "__main__":
    main()
