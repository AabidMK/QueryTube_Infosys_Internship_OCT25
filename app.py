from fastapi import FastAPI, UploadFile, File, HTTPException, Query
import pandas as pd
import chromadb
from chromadb.utils import embedding_functions
import ast
import io
from tqdm import tqdm
import os

app = FastAPI(title="🎬 YouTube ChromaDB Management API")

# Global DB path
DB_PATH = "./chroma_db"
COLLECTION_NAME = "youtube_videos"

# ---------------------------------------------------
# Helper functions
# ---------------------------------------------------
def parse_embedding(e):
    """Convert stringified embeddings back to float lists."""
    try:
        if isinstance(e, list):
            return e
        if pd.isna(e):
            return None
        return list(ast.literal_eval(str(e)))
    except Exception:
        return None

def clean_numeric_column(series):
    """Convert to int safely, replacing bad values."""
    return (
        series.replace(["nan", "NaN", None, "None", "", " "], 0)
        .fillna(0)
        .astype(float)
        .astype(int)
        .astype(str)
    )

def db_exists():
    """Check if ChromaDB folder exists."""
    return os.path.exists(DB_PATH) and len(os.listdir(DB_PATH)) > 0

# ---------------------------------------------------
# Initialize Chroma client (lazy)
# ---------------------------------------------------
def get_client():
    if not db_exists():
        raise HTTPException(status_code=400, detail="❌ Database not found. Please create the DB first.")
    return chromadb.PersistentClient(path=DB_PATH)

# ---------------------------------------------------
# Create Database (Initial Upload)
# ---------------------------------------------------
@app.post("/create_db")
async def create_db(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode("utf-8")))
        print(f"✅ Loaded CSV with {len(df)} rows")

        required_cols = ["id", "transcript", "embedding", "title", "channel_title", "viewCount", "duration_seconds"]
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            raise HTTPException(status_code=400, detail=f"Missing columns: {missing}")

        # Clean + Parse
        df["embedding"] = df["embedding"].apply(parse_embedding)
        df = df[df["embedding"].notna()].reset_index(drop=True)
        df["viewCount"] = clean_numeric_column(df["viewCount"])
        df["duration_seconds"] = clean_numeric_column(df["duration_seconds"])

        # Prepare data
        ids = df["id"].astype(str).tolist()
        embeddings = df["embedding"].tolist()
        documents = df["transcript"].astype(str).tolist()
        metadatas = df[["title", "channel_title", "viewCount", "duration_seconds"]].rename(
            columns={"duration_seconds": "duration"}
        ).to_dict(orient="records")

        client = chromadb.PersistentClient(path=DB_PATH)

        # Delete existing DB if any
        try:
            client.delete_collection(COLLECTION_NAME)
            print("🗑️ Old collection deleted successfully.")
        except Exception:
            pass

        collection = client.get_or_create_collection(COLLECTION_NAME)
        print("📦 Created new collection 'youtube_videos'")

        # Insert in batches
        BATCH_SIZE = 1000
        for start in tqdm(range(0, len(ids), BATCH_SIZE), desc="🚀 Inserting batches"):
            end = min(start + BATCH_SIZE, len(ids))
            collection.add(
                ids=ids[start:end],
                embeddings=embeddings[start:end],
                documents=documents[start:end],
                metadatas=metadatas[start:end]
            )

        return {"status": "success", "records_added": len(ids), "total_records": collection.count()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------------------------------
# Upload new CSV and insert more records
# ---------------------------------------------------
@app.post("/upload_csv")
async def upload_csv(file: UploadFile = File(...)):
    if not db_exists():
        raise HTTPException(status_code=400, detail="❌ Database not found. Please create it first using /create_db")

    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode("utf-8")))

        required_cols = ["id", "transcript", "embedding", "title", "channel_title", "viewCount", "duration_seconds"]
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            raise HTTPException(status_code=400, detail=f"Missing columns: {missing}")

        df["embedding"] = df["embedding"].apply(parse_embedding)
        df = df[df["embedding"].notna()].reset_index(drop=True)
        df["viewCount"] = clean_numeric_column(df["viewCount"])
        df["duration_seconds"] = clean_numeric_column(df["duration_seconds"])

        ids = df["id"].astype(str).tolist()
        embeddings = df["embedding"].tolist()
        documents = df["transcript"].astype(str).tolist()
        metadatas = df[["title", "channel_title", "viewCount", "duration_seconds"]].rename(
            columns={"duration_seconds": "duration"}
        ).to_dict(orient="records")

        client = get_client()
        collection = client.get_or_create_collection(COLLECTION_NAME)

        BATCH_SIZE = 1000
        for start in tqdm(range(0, len(ids), BATCH_SIZE), desc="🚀 Adding records"):
            end = min(start + BATCH_SIZE, len(ids))
            collection.add(
                ids=ids[start:end],
                embeddings=embeddings[start:end],
                documents=documents[start:end],
                metadatas=metadatas[start:end]
            )

        total = collection.count()
        return {"status": "success", "inserted": len(ids), "total_records": total}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------------------------------
# Search Videos
# ---------------------------------------------------
@app.get("/search")
def search_videos(query: str = Query(..., description="Search query text")):
    if not db_exists():
        raise HTTPException(status_code=400, detail="❌ Database not found. Please create it first using /create_db")

    embed_fn = embedding_functions.DefaultEmbeddingFunction()
    client = get_client()
    collection = client.get_collection(COLLECTION_NAME, embedding_function=embed_fn)

    results = collection.query(
        query_texts=[query],
        n_results=5,
        include=["metadatas", "distances", "documents"]
    )

    if not results["ids"]:
        return {"results": []}

    formatted_results = []
    for i, (vid, meta, dist) in enumerate(zip(results["ids"][0], results["metadatas"][0], results["distances"][0])):
        similarity_score = round(1 - dist, 3)
        formatted_results.append({
            "rank": i + 1,
            "video_id": vid,
            "title": meta.get("title", "Unknown Title"),
            "channel_title": meta.get("channel_title", "Unknown Channel"),
            "similarity_score": similarity_score,
            "video_url": f"https://www.youtube.com/watch?v={vid}"
        })

    return {"query": query, "results": formatted_results}

# ---------------------------------------------------
# Delete records by ID
# ---------------------------------------------------
@app.post("/delete_records")
async def delete_records(ids: list[str]):
    if not db_exists():
        raise HTTPException(status_code=400, detail="❌ Database not found. Please create it first using /create_db")

    try:
        client = get_client()
        collection = client.get_collection(COLLECTION_NAME)

        # Fetch records for backup
        records = collection.get(ids=ids)
        if not records or len(records["ids"]) == 0:
            raise HTTPException(status_code=404, detail="No matching records found.")

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

        backup_df = pd.DataFrame(backup_data)
        backup_df.to_csv("deleted_records_backup.csv", index=False, encoding="utf-8")

        # Delete from Chroma
        collection.delete(ids=ids)

        return {
            "status": "deleted",
            "records_deleted": len(ids),
            "backup_file": "deleted_records_backup.csv",
            "remaining_records": collection.count()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------------------------------
# Health Check
# ---------------------------------------------------
@app.get("/health")
def health_check():
    exists = db_exists()
    return {
        "status": "ok" if exists else "missing",
        "collection_name": COLLECTION_NAME if exists else None,
        "record_count": get_client().get_collection(COLLECTION_NAME).count() if exists else 0
    }
