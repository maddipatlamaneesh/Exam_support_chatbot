from Retrieval.retriever import retrieve


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

Answer the user's question using the provided context.

Instructions:
1. Use the provided context to answer.
2. Explain concepts clearly and accurately.
3. Do not invent information.
4. If the answer is not available in the context, say so.

Context:
{context}

User Question:
{query}

Answer:
"""

    return prompt


def generate_answer(query):

    # Step 1: Retrieve relevant chunks
    results = retrieve(query)

    # Step 2: Prepare context
    context = prepare_context(results)

    # Step 3: Build prompt
    prompt = build_prompt(query, context)

    return prompt