
import chromadb

# --------------------------------
# Connect to existing ChromaDB
# --------------------------------
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="youtube_videos")

print("✅ Connected to ChromaDB collection:", collection.name)
print("📊 Total videos stored:", collection.count())

# --------------------------------
# User Query Input
# --------------------------------
query = input("\n🔍 Enter your search query: ")

# --------------------------------
# Semantic Search
# --------------------------------
results = collection.query(
    query_texts=[query],
    n_results=5  # Number of top results to return
)

# --------------------------------
# Display Results
# --------------------------------
print("\n🎯 Top Search Results:\n")

for i in range(len(results["ids"][0])):
    meta = results["metadatas"][0][i]
    doc = results["documents"][0][i][:300]  # show first 300 chars of transcript

    print(f"Result #{i+1}")
    print("📺 Title:", meta.get("title", "N/A"))
    print("📣 Channel:", meta.get("channel_title", "N/A"))
    print("👁️ Views:", meta.get("view_count", "N/A"))
    print("⏱️ Duration:", meta.get("duration", "N/A"))
    print("🧠 Transcript snippet:", doc)
    print("-" * 80)

print("\n✅ Query complete!")
