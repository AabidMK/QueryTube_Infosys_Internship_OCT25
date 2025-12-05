import pandas as pd
import chromadb
from chromadb.config import Settings
import ast
from sentence_transformers import SentenceTransformer
import os

# =============================
# LOAD DATASET CSV
# =============================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "masterdataset_with_embeddings.csv")

df = pd.read_csv(CSV_PATH, on_bad_lines="skip", encoding="utf-8")
print("✅ CSV loaded successfully!")

# Clean ID and embedding column
df["id"] = df["id"].astype(str)
df = df.dropna(subset=["id", "embedding"])
df = df[df["id"] != "nan"]
df = df.drop_duplicates(subset=["id"]).reset_index(drop=True)

# Convert embedding from string → list
if isinstance(df["embedding"].iloc[0], str):
    df["embedding"] = df["embedding"].apply(lambda x: ast.literal_eval(x))

embedding_dim = len(df["embedding"].iloc[0])
print(f"🧩 Embedding dimension detected: {embedding_dim}")

# =============================
# CREATE VECTOR DB COLLECTION
# =============================

client = chromadb.Client(Settings(anonymized_telemetry=False))
collection_name = "youtube_video_embeddings"

# If exists → delete & recreate
if collection_name in [c.name for c in client.list_collections()]:
    client.delete_collection(name=collection_name)

collection = client.create_collection(name=collection_name)

collection.add(
    ids=df["id"].tolist(),
    embeddings=df["embedding"].tolist(),
    metadatas=[
        {
            "title": str(row.get("title", "")),
            "channel_title": str(row.get("channel_title", "")),
            "view_count": str(row.get("viewCount", "0")),
            "like_count": str(row.get("likeCount", "0")),
            "duration": str(row.get("duration", "")),
        }
        for _, row in df.iterrows()
    ],
)

print(f"✅ Inserted {len(df)} videos into the vector database.\n")

# =============================
# CHOOSE EMBEDDING MODEL
# =============================

if embedding_dim == 384:
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
elif embedding_dim == 768:
    model_name = "sentence-transformers/all-mpnet-base-v2"
else:
    model_name = "sentence-transformers/all-mpnet-base-v2"

model = SentenceTransformer(model_name)
print(f"🧠 Using embedding model: {model_name}\n")


# =============================
# INTERACTIVE TERMINAL SEARCH
# =============================
if __name__ == "__main__":
    print("💬 Type your search query below:\n")

    while True:
        user_query = input("🔍 Enter search: ").strip()

        if user_query.lower() in ["exit", "quit"]:
            print("\n👋 Goodbye!")
            break

        query_embedding = model.encode(user_query).tolist()
        results = collection.query(query_embeddings=[query_embedding], n_results=5)

        print(f"\nTop 5 results for '{user_query}':\n")

        for i in range(len(results["ids"][0])):
            video_id = results["ids"][0][i]
            meta = results["metadatas"][0][i]
            score = results["distances"][0][i]

            print(f"{i+1}. 🎬 {meta.get('title', 'N/A')}")
            print(f"   ID: {video_id}")
            print(f"   Channel: {meta.get('channel_title', 'N/A')}")
            print(f"   Views: {meta.get('view_count', 'N/A')}")
            print(f"   Likes: {meta.get('like_count', 'N/A')}")
            print(f"   Similarity: {score:.4f}")
            print("-" * 60)
        print("\n")


# ======================================================
# FASTAPI-CALLABLE FUNCTION  (THIS IS WHAT FRONTEND USES)
# ======================================================

def run_semantic_search(query: str):
    """Used by FastAPI to return top 5 semantic search results."""

    # Compute embedding
    query_embedding = model.encode(query).tolist()

    # Search ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5
    )

    output = []
    for i in range(len(results["ids"][0])):

        video_id = results["ids"][0][i]
        meta = results["metadatas"][0][i]
        similarity = results["distances"][0][i]

        # Build output object
        output.append({
            "id": video_id,
            "title": meta.get("title", ""),
            "channel_title": meta.get("channel_title", ""),
            "viewCount": meta.get("view_count", "0"),
            "likes": meta.get("like_count", "0"),
            "duration": meta.get("duration", ""),
            "similarity": float(similarity),
            "thumbnail": f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
        })

    return output
