"""
Docstring for 03-vector-search.movie_recs
"""

import os
import sys
import torch
from pymongo import MongoClient
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer


load_dotenv()
os.system("clear")


# Make Database Connection
print("[+] 🛜 Connectiong to Database")
client: MongoClient | None = None
db = None
collection = None
try:
    client = MongoClient(os.getenv("MONGODB_URI"))
    db = client.sample_mflix
    collection = db.movies
    print("[+] Connection Successful")
except Exception as e:
    print(f"[-] 🛜 Connectiong to Database Failed: {e}")
    sys.exit(1)

# PRINT EXAMPLE DOCUMENTS
# items = collection.find().limit(3)

# for item in items:
#     print(item)


device = "mps" if torch.backends.mps.is_available() else "cpu"


# GENERATE EMBEDDINGS
def generate_embedding(text: str) -> list[float]:
    """Generate an embedding for a given text."""
    model = SentenceTransformer(
        "sentence-transformers/all-MiniLM-L6-v2", device=device, local_files_only=True
    )

    embeddings = model.encode(text)
    # Convert NumPy array to list for BSON compatibility
    return embeddings.tolist()


# print(generate_embedding("Hello World"))

# GENERATE EMBEDDINGS FOR FIRST 50 DOCUMENTS
# for doc in collection.find({"plot": {"$exists": 1}}).limit(50):
#     print(f"\nMovie Name: {doc['title']}")

#     embedding = generate_embedding(doc["plot"])
#     doc["plot_embedding_hf"] = embedding

#     collection.replace_one({"_id": doc["_id"]}, doc)

#     print(f"{embedding[0:10]} ...")

# PERFORM THE QUERY
query = "action movies"

results = collection.aggregate(
    [
        {
            "$vectorSearch": {
                "queryVector": generate_embedding(query),
                "path": "plot_embedding_hf",
                "numCandidates": 100,
                "limit": 4,
                "index": "plot_search",
            }
        }
    ]
)
print(results.address)
# print(results.to_list()[0])

for result in results:
    print(f"Movie Name: {result['title']}")
    print(f"Plot: {result['plot']}")
    print("-" * 50)
