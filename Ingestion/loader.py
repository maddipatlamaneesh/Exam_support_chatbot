import pymupdf
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PDF_DIR = BASE_DIR / "DATA" / "pdf"


def resolve_pdf_path(pdf_path):
    """Return an existing PDF path, preserving the CLI's DATA/pdf fallback."""
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        pdf_path = PDF_DIR / pdf_path

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF not found: {pdf_path}"
        )

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError("Only PDF files can be ingested.")

    return pdf_path


def load_pdf(pdf_path, source_name=None):
    """Extract non-empty PDF pages and retain their source and page metadata."""
    pdf_path = resolve_pdf_path(pdf_path)

    documents = []

    with pymupdf.open(pdf_path) as doc:

        for page_number, page in enumerate(doc):

            text = page.get_text("text")

            if text.strip():

                documents.append({
                    "text": text,
                    "metadata": {
                        "source": source_name or pdf_path.name,
                        "page": page_number + 1
                    }
                })

    if not documents:
        raise ValueError(
            f"No extractable text was found in PDF: {source_name or pdf_path.name}"
        )

    return documents
