import os
from dotenv import load_dotenv
from google import genai

from Retrieval.retriever import retrieve


load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")

client = genai.Client(api_key=API_KEY)

MODEL_NAME = "gemini-3.6-flash"


def prepare_context(results):

    context = ""

    for i, result in enumerate(results):

        context += f"""
Context {i + 1}:
Source: {result["metadata"]["source"]}
Page: {result["metadata"]["page"]}

Content:
{result["document"]}
"""

    return context


def build_prompt(query, context):

    prompt = f"""
You are an AI exam assistant.

IMPORTANT INSTRUCTIONS:

1. Answer ONLY using the provided context.
2. Do not use your pretrained knowledge.
3. Do not add information that is not supported by the context.
4. If the answer is not available in the context, respond:
   "The requested information is not available in the uploaded PDFs."
5. Explain concepts clearly and in a student-friendly manner.
6. Do not make assumptions or invent information.

CONTEXT:
{context}

USER QUESTION:
{query}

ANSWER:
"""

    return prompt


def generate_answer(query):

    # Step 1: Retrieve relevant chunks
    results = retrieve(query)

    if not results:
        return "No relevant information found in the uploaded documents."

    # Step 2: Prepare context
    context = prepare_context(results)

    # Step 3: Build prompt
    prompt = build_prompt(query, context)

    # Step 4: Generate answer using Gemini
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    # Step 5: Return answer
    return response.text