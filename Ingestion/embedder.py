from sentence_transformers import SentenceTransformer

# Load the embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_embeddings(texts):

    embeddings = model.encode(texts)

    print("\n========== EMBEDDING SUMMARY ==========")
    print("Total embeddings:", len(embeddings))
    print("Embedding dimensions:", embeddings.shape[1])

    return embeddings