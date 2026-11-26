from Ingestion.embedder import generate_embeddings
from Ingestion.vector_store import client


def retrieve(query, collection_name=None, top_k=5):

    if not query.strip():
        raise ValueError("Query cannot be empty")

    # Step 1: Generate query embedding
    query_embedding = generate_embeddings([query])

    all_results = []

    # Step 2: Select collections
    if collection_name:

        collections = [
            client.get_collection(name=collection_name)
        ]

    else:

        collections = client.list_collections()

        collections = [
            client.get_collection(
                name=c if isinstance(c, str) else c.name
            )
            for c in collections
        ]

    # Step 3: Search selected collections
    for collection in collections:

        count = collection.count()

        if count == 0:
            continue

        results = collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=min(top_k, count),
            include=[
                "documents",
                "metadatas",
                "distances"
            ]
        )

        # Step 4: Extract results
        for i in range(len(results["ids"][0])):

            all_results.append({

                "id": results["ids"][0][i],

                "document": results["documents"][0][i],

                "metadata": results["metadatas"][0][i],

                "distance": results["distances"][0][i],

                "collection": collection.name

            })

    # Step 5: Sort by similarity distance
    all_results.sort(
        key=lambda x: x["distance"]
    )

    # Step 6: Return top K
    return all_results[:top_k]