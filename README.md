# AI Exam Support Chatbot

A multi-document Retrieval-Augmented Generation (RAG) application for asking
exam-study questions about PDF material. It uses PyMuPDF for extraction,
LangChain recursive splitting, Sentence Transformers embeddings, ChromaDB
persistence, and Google Gemini for answer generation.

## Run the Streamlit application

1. Create and activate a Python virtual environment (Python 3.11 is used in
   this project).
2. Install the dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

3. Add a Gemini API key to `.env`:

   ```env
   GEMINI_API_KEY=your_key_here
   ```

4. Start the application from the project root:

   ```powershell
   streamlit run frontend/app.py
   ```

## How document isolation works

- Upload PDFs directly in the browser; there is no need to copy them into
  `DATA/pdf`.
- Each upload is saved under `DATA/uploads/`, which is ignored by Git.
- Each PDF is assigned its own persistent ChromaDB collection. A readable
  filename prefix and a SHA-256 content hash form the collection identifier,
  preventing two different files with the same filename from overwriting each
  other.
- Uploading the same file again refreshes that document's collection instead
  of creating duplicate chunks.
- The document dropdown shows filenames rather than collection identifiers.
  When names collide, the UI appends a short identifier to distinguish them.
- A question is always retrieved from the currently selected document only.

Existing files in `DATA/pdf` can still be ingested with the original command
line flow:

```powershell
python main.py
```
