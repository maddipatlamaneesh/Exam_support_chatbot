from Ingestion.pipeline import ingest_pdf


if __name__ == "__main__":

    pdf_name = input("Enter PDF filename: ")

    ingest_pdf(pdf_name)