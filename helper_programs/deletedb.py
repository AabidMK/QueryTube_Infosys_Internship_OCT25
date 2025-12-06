
import chromadb

# Initialize Chroma client pointing to your local DB folder
client = chromadb.PersistentClient(path="./chroma_db")

# Delete the old collection by name
try:
    client.delete_collection("youtube_videos")
    print("🗑️ Successfully deleted Chroma collection: youtube_videos")
except Exception as e:
    print(f"⚠️ No existing collection found or already deleted: {e}")
