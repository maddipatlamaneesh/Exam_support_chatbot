import chromadb

client=chromadb.PersistentClient(
    path="./My_Database"
)

#collection
collection = client.get_or_create_collection(
    name="python_notes"
)

print("client created sucessfully")
collections = client.list_collections()

print(collections)