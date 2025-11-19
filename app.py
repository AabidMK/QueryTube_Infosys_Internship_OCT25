from fastapi import FastAPI, UploadFile, File, HTTPException, Query, Depends
import pandas as pd
import chromadb
from chromadb.utils import embedding_functions
import ast, io, os
from tqdm import tqdm
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Import summarization functionality
from summarize import get_transcript_from_db, summarize_text



app = FastAPI(title="🎬 Multi-DB Chroma Manager (Dynamic, String-Based)")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "./chroma_db"

# ---------------------------------------------------
# Helper Functions
# ---------------------------------------------------
def get_client():
    """Initialize Chroma client and ensure DB path exists."""
    if not os.path.exists(DB_PATH):
        os.makedirs(DB_PATH)
    return chromadb.PersistentClient(path=DB_PATH)

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

def list_databases():
    """Return available Chroma collections."""
    client = get_client()
    return [c.name for c in client.list_collections()]

def validate_db_name(name: str):
    """Ensure selected DB exists."""
    available = list_databases()
    if name not in available:
        raise HTTPException(status_code=404, detail=f"Database '{name}' not found. Available: {available}")
    return name

# ---------------------------------------------------
# 🧱 Create a new ChromaDB collection
# ---------------------------------------------------
@app.post("/create_db")
async def create_db(collection_name: str = Query(..., description="Name of new database"),
                    file: UploadFile = File(...)):
    """Create a new database and insert data from CSV."""
    contents = await file.read()
    df = pd.read_csv(io.StringIO(contents.decode("utf-8")))
    print(f"✅ Loaded CSV with {len(df)} rows for '{collection_name}'")

    required_cols = ["id", "transcript", "embedding", "title", "channel_title", "viewCount", "duration_seconds"]
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing columns: {missing}")

    # Clean data
    df["embedding"] = df["embedding"].apply(parse_embedding)
    df = df[df["embedding"].notna()].reset_index(drop=True)
    df["viewCount"] = clean_numeric_column(df["viewCount"])
    df["duration_seconds"] = clean_numeric_column(df["duration_seconds"])

    ids = df["id"].astype(str).tolist()
    embeddings = df["embedding"].tolist()
    documents = df["transcript"].astype(str).tolist()
    metadatas = df[["title", "channel_title", "viewCount", "duration_seconds"]] \
        .rename(columns={"duration_seconds": "duration"}).to_dict(orient="records")

    client = get_client()
    try:
        client.delete_collection(collection_name)
        print(f"🗑️ Existing collection '{collection_name}' deleted.")
    except:
        pass

    collection = client.get_or_create_collection(collection_name)
    print(f"📦 Created new collection '{collection_name}'")

    # Batch insert
    BATCH_SIZE = 1000
    for start in tqdm(range(0, len(ids), BATCH_SIZE), desc=f"🚀 Inserting to {collection_name}"):
        end = min(start + BATCH_SIZE, len(ids))
        collection.add(
            ids=ids[start:end],
            embeddings=embeddings[start:end],
            documents=documents[start:end],
            metadatas=metadatas[start:end]
        )

    return {"status": "success", "collection": collection_name, "records_added": len(ids)}

# ---------------------------------------------------
# 📤 Upload CSV to existing DB
# ---------------------------------------------------
@app.post("/upload_csv")
async def upload_csv(collection_name: str = Query(..., description="Enter DB name (see /health for list)"),
                     file: UploadFile = File(...)):
    """Insert additional data into an existing DB."""
    collection_name = validate_db_name(collection_name)
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
    metadatas = df[["title", "channel_title", "viewCount", "duration_seconds"]] \
        .rename(columns={"duration_seconds": "duration"}).to_dict(orient="records")

    client = get_client()
    collection = client.get_collection(collection_name)

    BATCH_SIZE = 1000
    for start in tqdm(range(0, len(ids), BATCH_SIZE), desc=f"📥 Adding to {collection_name}"):
        end = min(start + BATCH_SIZE, len(ids))
        collection.add(
            ids=ids[start:end],
            embeddings=embeddings[start:end],
            documents=documents[start:end],
            metadatas=metadatas[start:end]
        )

    return {"status": "success", "inserted_records": len(ids), "collection": collection_name}

# ---------------------------------------------------
# 🔍 Search Videos
# ---------------------------------------------------
@app.get("/search")
def search_videos(collection_name: str = Query(..., description="Enter DB name (see /health)"),
                  query: str = Query(..., description="Enter search query")):
    """Perform semantic search inside the selected DB."""
    collection_name = validate_db_name(collection_name)
    client = get_client()
    embed_fn = embedding_functions.DefaultEmbeddingFunction()
    collection = client.get_collection(collection_name, embedding_function=embed_fn)

    results = collection.query(query_texts=[query], n_results=5,
                               include=["metadatas", "distances", "documents"])

    formatted = []
    for i, (vid, meta, dist) in enumerate(zip(results["ids"][0], results["metadatas"][0], results["distances"][0])):
        formatted.append({
            "rank": i + 1,
            "video_id": vid,
            "title": meta.get("title", "Unknown Title"),
            "channel": meta.get("channel_title", "Unknown Channel"),
            "similarity_score": round(1 - dist, 3),
            "video_url": f"https://www.youtube.com/watch?v={vid}"
        })

    return {"collection": collection_name, "query": query, "results": formatted}

# ---------------------------------------------------
# 🗑️ Delete Records
# ---------------------------------------------------
@app.post("/delete_records")
async def delete_records(collection_name: str = Query(..., description="Enter DB name (see /health)"),
                         ids: List[str] = Query(..., description="List of video IDs to delete")):
    """Delete records and back them up."""
    collection_name = validate_db_name(collection_name)
    client = get_client()
    collection = client.get_collection(collection_name)

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
    backup_file = f"deleted_{collection_name}_backup.csv"
    backup_df.to_csv(backup_file, index=False, encoding="utf-8")

    collection.delete(ids=ids)

    return {"status": "deleted", "collection": collection_name,
            "records_deleted": len(ids), "backup": backup_file}

# ---------------------------------------------------
# 📝 Summarize Video Transcript
# ---------------------------------------------------
class SummaryRequest(BaseModel):
    video_id: str
    collection_name: str
    transcript: Optional[str] = None  # Make transcript optional

@app.post("/summarize")
async def summarize_video(request: SummaryRequest):
    """Always fetch transcript from database, ignore request.transcript."""

    try:
        # Always fetch transcript from DB
        transcript = get_transcript_from_db(
            request.video_id,
            request.collection_name
        )

        # Validate
        if not transcript or transcript.strip() == "":
            raise HTTPException(
                status_code=404,
                detail="Transcript not found in the database"
            )

        # Summarize
        summary = summarize_text(transcript)

        return {"summary": summary}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating summary: {str(e)}"
        )


# ---------------------------------------------------
# 🩺 Health Endpoint
# ---------------------------------------------------
@app.get("/health")
async def health_check():
    """List all databases and record counts."""
    client = get_client()
    collections = client.list_collections()
    result = []
    for collection in collections:
        try:
            count = collection.count()
            result.append({
                "name": collection.name,
                "record_count": count
            })
        except Exception as e:
            print(f"Error getting count for {collection.name}: {e}")
            result.append({
                "name": collection.name,
                "record_count": 0,
                "error": str(e)
            })
    return {"databases": result}




@app.delete("/delete_db")
async def delete_db(collection_name: str = Query(..., description="Name of the database to delete")):
    """Delete a database collection."""
    try:
        client = get_client()
        client.delete_collection(collection_name)
        return JSONResponse(
            status_code=200,
            content={"status": "success", "message": f"Database '{collection_name}' deleted successfully"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete database: {str(e)}"
        )