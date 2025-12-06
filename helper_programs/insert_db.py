from fastapi import FastAPI, UploadFile, File, HTTPException
import pandas as pd
import chromadb
import ast
import io
from tqdm import tqdm

app = FastAPI(title="📦 ChromaDB CSV Uploader")

# -----------------------------
# Connect to Persistent ChromaDB
# -----------------------------
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("youtube_videos")
print("✅ Connected to existing collection: youtube_videos")

# -----------------------------
# Helper: Parse embedding safely
# -----------------------------
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

# -----------------------------
# Helper: Clean numeric columns
# -----------------------------
def clean_numeric_column(series):
    """Convert to int safely, replacing bad values."""
    return (
        series.replace(["nan", "NaN", None, "None", "", " "], 0)
        .fillna(0)
        .astype(float)
        .astype(int)
        .astype(str)
    )

# -----------------------------
# API: Upload and Insert CSV
# -----------------------------
@app.post("/upload_csv")
async def upload_csv(file: UploadFile = File(...)):
    try:
        # Step 1: Read file
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode("utf-8")))
        print(f"✅ Uploaded CSV with {len(df)} rows")

        # Step 2: Check required columns
        required_cols = ["id", "transcript", "embedding", "title", "channel_title", "viewCount", "duration_seconds"]
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            raise HTTPException(status_code=400, detail=f"Missing columns: {missing}")

        # Step 3: Clean & parse
        df["embedding"] = df["embedding"].apply(parse_embedding)
        df = df[df["embedding"].notna()].reset_index(drop=True)
        df["viewCount"] = clean_numeric_column(df.get("viewCount", pd.Series([0]*len(df))))
        df["duration_seconds"] = clean_numeric_column(df.get("duration_seconds", pd.Series([0]*len(df))))

        # Step 4: Prepare for Chroma
        ids = df["id"].astype(str).tolist()
        embeddings = df["embedding"].tolist()
        documents = df["transcript"].astype(str).tolist()
        metadatas = df[["title", "channel_title", "viewCount", "duration_seconds"]].rename(
            columns={"duration_seconds": "duration"}
        ).to_dict(orient="records")

        # Step 5: Insert to Chroma in batches
        BATCH_SIZE = 1000
        for start in tqdm(range(0, len(ids), BATCH_SIZE), desc="🚀 Inserting batches"):
            end = min(start + BATCH_SIZE, len(ids))
            collection.add(
                ids=ids[start:end],
                embeddings=embeddings[start:end],
                documents=documents[start:end],
                metadatas=metadatas[start:end]
            )

        total = collection.count()
        return {"status": "success", "inserted_records": len(ids), "total_records": total}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------
# Health Check
# -----------------------------
@app.get("/health")
def health_check():
    return {"status": "ok", "total_records": collection.count()}
