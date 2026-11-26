from Ingestion.pipeline import ingest_pdf
from Generator.generator import generate_answer


def main():

    while True:

        print("\n========== AI EXAM SUPPORT CHATBOT ==========")
        print("1. Ingest PDFs")
        print("2. Ask a Question")
        print("3. Exit")

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":

            try:
                n = int(input("\nEnter number of PDFs: "))

                if n <= 0:
                    print("Please enter a valid number.")
                    continue

                for i in range(n):

                    pdf_name = input(
                        f"\nEnter PDF {i + 1} filename: "
                    ).strip()

                    try:
                        ingest_pdf(pdf_name)
                        print(f"{pdf_name} ingested successfully!")

                    except Exception as e:
                        print(f"Failed to ingest {pdf_name}:", e)

                print("\nPDF ingestion process completed!")

            except ValueError:
                print("Please enter a valid number.")

        elif choice == "2":

            print("\n========== CHATBOT ==========")
            print("Type 'exit' to return to the main menu.")

            while True:

                query = input("\nYou: ").strip()

                if query.lower() == "exit":
                    break

                if not query:
                    print("Please enter a question.")
                    continue

                try:
                    answer = generate_answer(query)

                    print("\nAI Assistant:")
                    print(answer)

                except Exception as e:
                    print("\nError:", e)

        elif choice == "3":

            print("\nThank you for using AI Exam Support Chatbot!")
            break

        else:
            print("\nInvalid choice. Please try again.")


if __name__ == "__main__":
    main()