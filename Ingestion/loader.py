import pymupdf
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PDF_DIR = BASE_DIR / "DATA" / "pdf"


def load_pdf(pdf_path):

    pdf_path = Path(pdf_path)

    # Support existing CLI filenames
    if not pdf_path.exists():
        pdf_path = PDF_DIR / pdf_path

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF not found: {pdf_path}"
        )

    documents = []

    with pymupdf.open(pdf_path) as doc:

        for page_number, page in enumerate(doc):

            text = page.get_text("text")

            if text.strip():

                documents.append({
                    "text": text,
                    "metadata": {
                        "source": pdf_path.name,
                        "page": page_number + 1
                    }
                })

    return documents