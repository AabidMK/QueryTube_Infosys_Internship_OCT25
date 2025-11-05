import faiss
import pickle 
from sentence_transformers import SentenceTransformer
# Load the saved FAISS index and metadata
index = faiss.read_index("final_embeddings.index")

with open("final_metadata.pkl", "rb") as f:
    metadata = pickle.load(f)

# Load the same embedding model used for encoding
model = SentenceTransformer("all-MiniLM-L6-v2")

def semantic_search(query, top_k=5):
    # Encode the query
    query_vector = model.encode([query], convert_to_numpy=True).astype("float32")

    # Normalize for cosine similarity
    faiss.normalize_L2(query_vector)

    # Search in the FAISS index
    distances, indices = index.search(query_vector, top_k)

    # Display results
    print(f"\nTop {top_k} results for query: '{query}'\n")

    for i, idx in enumerate(indices[0]):
        result = metadata[idx]

        # Handle missing fields gracefully
        title = str(result.get("title", "Untitled"))
        vid_id = str(result.get("id", ""))
        channel = str(result.get("channel_title", "Unknown"))

        print(f"{i + 1}. Title: {title}")
        print(f"   Channel: {channel}")
        print(f"   Id:{vid_id}")
        print(f"   https://www.youtube.com/watch?v={vid_id}")
        print(f"   Similarity Score: {distances[0][i]:.4f}\n")
        


#  Example search
query = input("Enter query: ")
semantic_search(query, top_k=5)