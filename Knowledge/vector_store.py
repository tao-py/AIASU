import chromadb

client = chromadb.Client()

collection = client.create_collection("knowledge")

def add(text, embedding):

    collection.add(
        documents=[text],
        embeddings=[embedding]
    )

def search(embedding):

    return collection.query(
        query_embeddings=[embedding],
        n_results=3
    )