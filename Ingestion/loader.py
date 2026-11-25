import pymupdf
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
PDF_DIR = BASE_DIR / "DATA" / "pdf"


def load_pdf(pdf_name):

    pdf_path = PDF_DIR / pdf_name

    documents = []

    with pymupdf.open(pdf_path) as doc:

        total_pages = len(doc)

        for page_number, page in enumerate(doc):

            text = page.get_text("text")

            if text.strip():

                documents.append({
                    "text": text,
                    "metadata": {
                        "source": pdf_name,
                        "page": page_number + 1
                    }
                })

    pages_with_content = len(documents)
    pages_without_content = total_pages - pages_with_content

    print("\n========== PDF LOADING SUMMARY ==========")
    print("PDF:", pdf_name)
    print("Total pages:", total_pages)
    print("Pages with extracted content:", pages_with_content)
    print("Pages without extracted content:", pages_without_content)

    return documents


if __name__ == "__main__":

    documents = load_pdf("AI_Part1_Theory_Quick_Revision.pdf")