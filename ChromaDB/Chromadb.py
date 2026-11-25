import chromadb

client = chromadb.PersistentClient(
    path="./ChromaDB/My_Database"
)

# Get the existing collection
collection = client.get_collection(
    name="ai_part1_theory_quick_revision"
)

# Retrieve first records
result = collection.get(
    ids=["chunk_1"],
    include=["documents", "metadatas", "embeddings"]
)
print(result)