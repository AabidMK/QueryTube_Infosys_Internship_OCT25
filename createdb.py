
import pandas as pd
import numpy as np
import chromadb
import ast
from tqdm import tqdm

# === Step 1: Load your CSV file ===
CSV_PATH = "enriched_data_with_chunked_embeddings.csv"  # change if needed
df = pd.read_csv(CSV_PATH)
print(f"✅ Loaded CSV with {len(df)} rows")

# === Step 2: Parse embeddings ===
def parse_embedding(e):
    """Convert stringified embeddings back to float lists."""
    if isinstance(e, list):
        return e
    if pd.isna(e):
        return None
    try:
        return list(ast.literal_eval(str(e)))
    except Exception:
        return None

df["embedding"] = df["embedding"].apply(parse_embedding)
df = df[df["embedding"].notna()].reset_index(drop=True)
print(f"🧠 Valid embeddings found: {len(df)}")

# === Step 3: Ensure correct column names ===
required_cols = ["id", "transcript", "embedding", "title", "channel_title", "viewCount", "duration"]
for col in required_cols:
    if col not in df.columns:
        raise ValueError(f"❌ Missing required column in CSV: {col}")

# === Step 4: Prepare lists for Chroma ===
ids = df["id"].astype(str).tolist()
embeddings = df["embedding"].tolist()
documents = df["transcript"].astype(str).tolist()
metadatas = df[["title", "channel_title", "viewCount", "duration"]].to_dict(orient="records")

# === Step 5: Initialize Chroma ===
client = chromadb.PersistentClient(path="./chroma_db")

# Delete existing collection (keep model cache intact)
try:
    client.delete_collection("youtube_videos")
    print("🗑️ Old collection deleted successfully")
except Exception:
    print("⚠️ No existing collection found, creating new one")

collection = client.get_or_create_collection("youtube_videos")
print("📦 Created new collection 'youtube_videos'")

# === Step 6: Insert data in batches ===
BATCH_SIZE = 1000
for start in tqdm(range(0, len(ids), BATCH_SIZE), desc="🚀 Inserting batches"):
    end = min(start + BATCH_SIZE, len(ids))
    collection.add(
        ids=ids[start:end],
        embeddings=embeddings[start:end],
        documents=documents[start:end],
        metadatas=metadatas[start:end]
    )

print(f"✅ Finished! Total records in Chroma: {collection.count()}")
