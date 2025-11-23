import faiss
import pickle
from sentence_transformers import SentenceTransformer
import numpy as np

# Load FAISS index
index = faiss.read_index("final_embeddings.index")

# Load metadata
with open("final_metadata.pkl", "rb") as f:
    metadata = pickle.load(f)

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

def semantic_search(query, top_k=5):
    """Returns top-k search results in JSON-friendly structure."""

    # Encode query
    query_vector = model.encode([query], convert_to_numpy=True).astype("float32")

    # Normalize for cosine similarity
    faiss.normalize_L2(query_vector)

    # Search FAISS index
    distances, indices = index.search(query_vector, top_k)

    results = []

    for i, idx in enumerate(indices[0]):
        video = metadata[idx]
        results.append({
            "rank": i + 1,
            "id": video.get("id", ""),
            "title": video.get("title", "Untitled"),
            "description": video.get("description", "")[:200],  # trimmed
            "channel_title": video.get("channel_title", "Unknown"),
            "score": float(distances[0][i]),
            "likeCount": video.get("likeCount", "NA"),
            "viewCount": video.get("viewCount", "NA"),
            "youtube_url": f"https://www.youtube.com/watch?v={video.get('id', '')}"
        })

    return results



if __name__ == "__main__":
    q = input("Enter query: ")
    results = semantic_search(q)
    for r in results:
        print(r)
