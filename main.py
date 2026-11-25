from Ingestion.pipeline import ingest_pdf
from Generator.generator import generate_answer


def main():

    while True:

        print("\n========== AI EXAM SUPPORT CHATBOT ==========")
        print("1. Ingest PDF")
        print("2. Ask a Question")
        print("3. Exit")

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":

            pdf_name = input("Enter PDF filename: ").strip()

            try:
                ingest_pdf(pdf_name)
                print("\nPDF ingestion completed successfully!")

            except Exception as e:
                print("\nPDF ingestion failed:", e)

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