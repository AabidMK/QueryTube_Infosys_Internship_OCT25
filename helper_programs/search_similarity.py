
import chromadb
from chromadb.utils import embedding_functions

# === Step 1: Connect to ChromaDB ===
client = chromadb.PersistentClient(path="./chroma_db")

# Use Chroma’s optimized ONNX embedding model (MiniLM)
embed_fn = embedding_functions.DefaultEmbeddingFunction()

# Load collection
collection = client.get_collection("youtube_videos", embedding_function=embed_fn)

print(f"✅ Connected to ChromaDB collection: youtube_videos")
print(f"📊 Total videos stored: {collection.count()}\n")

# === Step 2: Accept user query ===
query = input("🔍 Enter your search query: ").strip()
if not query:
    print("❌ Please enter a valid query.")
    exit()

# === Step 3: Convert query → embedding and search ===
results = collection.query(
    query_texts=[query],
    n_results=5,
    include=["metadatas", "distances", "documents"]  # ✅ No "ids" here
)

# === Step 4: Display results ===
print("\n🎯 Top 5 Most Relevant Videos:\n")

ids = results["ids"][0]
metas = results["metadatas"][0]
distances = results["distances"][0]

for i in range(len(ids)):
    vid = ids[i]
    meta = metas[i]
    dist = distances[i]

    title = meta.get("title", "Unknown Title")
    channel = meta.get("channel_title", "Unknown Channel")
    similarity_score = round(1 - dist, 3)
    video_url = f"https://www.youtube.com/watch?v={vid}"

    print(f"{i+1}. 🎬 {title}")
    print(f"   🆔 Video ID: {vid}")
    print(f"   🔗 Video URL: {video_url}")
    print(f"   📣 Channel: {channel}")
    print(f"   🔹 Similarity Score: {similarity_score}")
    print("-" * 80)

print("\n✅ Query complete!")
