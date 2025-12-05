import chromadb
from chromadb.utils import embedding_functions

# === Step 1: Connect to ChromaDB ===
client = chromadb.PersistentClient(path="./chroma_db")

# Use Chroma's built-in ONNX embedding model (MiniLM)
embed_fn = embedding_functions.DefaultEmbeddingFunction()

# Load your existing collection with embedding function
collection = client.get_collection("youtube_videos", embedding_function=embed_fn)

print(f"✅ Connected to ChromaDB collection: youtube_videos")
print(f"📊 Total videos stored: {collection.count()}\n")

# === Step 2: Utility functions ===
def format_views(v):
    """Format view count into human-readable form."""
    try:
        if v is None or str(v).lower() in ["nan", "none", "n/a", ""]:
            return "N/A"
        v = float(v)
        if v >= 1_000_000:
            return f"{v/1_000_000:.1f}M"
        elif v >= 1_000:
            return f"{v/1_000:.1f}K"
        return str(int(v))
    except Exception:
        return "N/A"

def format_duration(seconds):
    """Convert seconds to mm:ss."""
    try:
        seconds = int(float(seconds))
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}:{secs:02d}"
    except Exception:
        return "N/A"

# === Step 3: User query ===
query = input("🔍 Enter your search query: ").strip()
if not query:
    print("❌ Please enter a valid query.")
    exit()

# === Step 4: Query ChromaDB ===
results = collection.query(
    query_texts=[query],
    n_results=5
)

# === Step 5: Display results ===
print("\n🎯 Top Search Results:\n")

if not results["metadatas"] or not results["metadatas"][0]:
    print("❌ No results found.")
else:
    for i, (metadata, doc) in enumerate(zip(results["metadatas"][0], results["documents"][0])):
        title = metadata.get("title", "Unknown Title")
        channel = metadata.get("channel_title", "Unknown Channel")
        views = format_views(metadata.get("viewCount", "N/A"))
        duration = format_duration(metadata.get("duration", "N/A"))
        snippet = (doc[:300].replace("\n", " ") + "...") if doc else "No transcript available."

        print(f"--------------------------------------------------------------------------------")
        print(f"Result #{i+1}")
        print(f"📺 Title: {title}")
        print(f"📣 Channel: {channel}")
        print(f"👁️ Views: {views}")
        print(f"⏱️ Duration: {duration}")
        print(f"🧠 Transcript snippet: {snippet}")
    print("--------------------------------------------------------------------------------")

print("\n✅ Query complete!")
