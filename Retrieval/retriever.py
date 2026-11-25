from Ingestion.embedder import generate_embeddings
from Ingestion.vector_store import client


def retrieve(query, top_k=5):

    if not query.strip():
        raise ValueError("Query cannot be empty")

    # Step 1: Generate query embedding
    query_embedding = generate_embeddings([query])

    # Step 2: Get all available collections
    collections = client.list_collections()

    all_results = []

    # Step 3: Search each collection
    for collection_info in collections:

        collection_name = (
            collection_info
            if isinstance(collection_info, str)
            else collection_info.name
        )

        collection = client.get_collection(name=collection_name)

        # Skip empty collections
        count = collection.count()

        if count == 0:
            continue

        results = collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=min(top_k, count),
            include=["documents", "metadatas", "distances"]
        )

        # Step 4: Extract results
        for i in range(len(results["ids"][0])):

            all_results.append({
                "id": results["ids"][0][i],
                "document": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
                "collection": collection_name
            })

    # Step 5: Sort results by distance
    all_results.sort(key=lambda x: x["distance"])

    # Step 6: Return global top K
    return all_results[:top_k]