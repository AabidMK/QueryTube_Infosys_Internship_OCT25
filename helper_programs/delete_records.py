import chromadb
import pandas as pd

# ------------------------------
# Connect to your ChromaDB
# ------------------------------
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection("youtube_videos")

# ------------------------------
# Step 1: Specify IDs to delete
# ------------------------------
video_ids_to_delete = [
    "bS9R6aCVEzw",  # example
    "DC2p3kFjcK0",
    "oAYuGx8BINI",
    "gdiao7L9GjE",
    "GW7B6vwktPA"
]

# ------------------------------
# Step 2: Fetch those records (for backup)
# ------------------------------
records = collection.get(ids=video_ids_to_delete)

if not records or len(records["ids"]) == 0:
    print("❌ No matching records found for given IDs.")
    exit()

# Extract relevant info
backup_data = []
for i in range(len(records["ids"])):
    backup_data.append({
        "id": records["ids"][i],
        "title": records["metadatas"][i].get("title", ""),
        "channel_title": records["metadatas"][i].get("channel_title", ""),
        "viewCount": records["metadatas"][i].get("viewCount", ""),
        "duration": records["metadatas"][i].get("duration", ""),
        "transcript": records["documents"][i]
    })

# Save to CSV
backup_df = pd.DataFrame(backup_data)
backup_df.to_csv("deleted_records_backup.csv", index=False, encoding="utf-8")
print(f"💾 Backup saved to deleted_records_backup.csv ({len(backup_df)} records)")

# ------------------------------
# Step 3: Delete them from ChromaDB
# ------------------------------
collection.delete(ids=video_ids_to_delete)
print("🗑️ Records deleted successfully from ChromaDB.")

# Verify
print(f"✅ Remaining records in DB: {collection.count()}")
