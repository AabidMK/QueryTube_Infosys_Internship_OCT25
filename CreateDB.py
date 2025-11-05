import pandas as pd
import numpy as np
import chromadb
import ast
from tqdm import tqdm
import uuid

CSV_PATH = "data_chunked_embeddings.csv"
df = pd.read_csv(CSV_PATH)
print(f"✅ Loaded CSV with {len(df)} rows")

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

required_cols = ["id", "transcript", "embedding", "title", "channel_title", "viewCount", "duration"]
for col in required_cols:
    if col not in df.columns:
        raise ValueError(f"❌ Missing required column in CSV: {col}")

# Diagnostics for problematic ids
nan_count = df["id"].isna().sum()
dup_count = df["id"].duplicated().sum()
print(f"🔍 id column - NaNs: {nan_count}, Duplicate rows: {dup_count}")

# Build unique string IDs (preserve original where possible)
seen = set()
final_ids = []
for i, raw in enumerate(df["id"]):
    # treat empty string or whitespace or actual NaN as missing
    if pd.isna(raw) or str(raw).strip() == "" or str(raw).lower() == "nan":
        new_id = str(uuid.uuid4())
    else:
        candidate = str(raw).strip()
        if candidate in seen:
            # make deterministic unique id by appending the row index
            new_id = f"{candidate}_{i}"
        else:
            new_id = candidate
    final_ids.append(new_id)
    seen.add(new_id)

# Final sanity checks
if len(final_ids) != len(df):
    raise RuntimeError("ID list length mismatch with dataframe")

if len(set(final_ids)) != len(final_ids):
    # this should not happen given the logic above
    raise RuntimeError("IDs are still not unique after processing")

ids = final_ids
embeddings = df["embedding"].tolist()
documents = df["transcript"].astype(str).tolist()
metadatas = df[["title", "channel_title", "viewCount", "duration"]].to_dict(orient="records")

# extra checks before sending to chroma
print("🔎 Sanity lengths -> ids:", len(ids), "embeddings:", len(embeddings),
      "documents:", len(documents), "metadatas:", len(metadatas))

# ensure every embedding is a list of numbers
bad_emb_idx = [i for i, e in enumerate(embeddings) if not (isinstance(e, list) and all(isinstance(x, (int, float)) for x in e))]
if bad_emb_idx:
    print("❌ Found invalid embeddings at indexes (first 10):", bad_emb_idx[:10])
    raise ValueError("Embeddings must be lists of numbers. Fix the CSV or embedding parsing.")

# connect to chroma and insert
client = chromadb.PersistentClient(path="./chroma_db")
try:
    client.delete_collection("youtube_videos")
    print("🗑️ Old collection deleted successfully")
except Exception:
    print("⚠️ No existing collection found, creating new one")

collection = client.get_or_create_collection("youtube_videos")
print("📦 Created new collection 'youtube_videos'")

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
