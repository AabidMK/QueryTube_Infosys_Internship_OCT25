from fastapi import FastAPI, UploadFile, File
import pandas as pd
import chromadb
from chromadb.config import Settings

# Import your two main functions
from summarize import summarize_video
from semantic_search import run_semantic_search

# =============================
# ADD CORS MIDDLEWARE (Required for React)
# =============================
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow all origins (React + any frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================
# 1. INITIALIZE CHROMA VECTOR DB
# =============================
client = chromadb.Client(Settings(anonymized_telemetry=False, is_persistent=False))
collection_name = "youtube_embeddings_fastapi"

collection = client.create_collection(
    name=collection_name,
    get_or_create=True
)

# =============================
# 2. HELPER FUNCTION: PARSE EMBEDDINGS
# =============================
def parse_embedding(x):
    if isinstance(x, str):
        x = x.strip("[]")
        try:
            return [float(i) for i in x.split(",") if i.strip()]
        except:
            return []
    return x


# =============================
# 3. CSV INGESTION ENDPOINT
# =============================
@app.post("/ingest")
async def ingest_csv(file: UploadFile = File(...)):

    try:
        df = pd.read_csv(file.file, on_bad_lines="skip", encoding="utf-8")

        required_cols = ["id", "transcript", "embedding", "title", "channel_title", "viewCount", "duration"]
        for col in required_cols:
            if col not in df.columns:
                return {"error": f"Missing required column: {col}"}

        # Clean ID column
        df["id"] = df["id"].astype(str)
        df["id"] = df["id"].replace("nan", "").replace("None", "")
        empty_mask = df["id"].str.strip() == ""
        df.loc[empty_mask, "id"] = [f"auto_id_{i}" for i in range(empty_mask.sum())]

        # Remove duplicates
        before = len(df)
        df = df.drop_duplicates(subset=["id"], keep="first").reset_index(drop=True)
        duplicates_removed = before - len(df)

        # Parse embeddings
        df["embedding"] = df["embedding"].apply(parse_embedding)

        # Store in ChromaDB
        collection.add(
            ids=df["id"].tolist(),
            embeddings=df["embedding"].tolist(),
            metadatas=[
                {
                    "title": row["title"],
                    "transcript": row["transcript"],
                    "channel_title": row["channel_title"],
                    "viewCount": row["viewCount"],
                    "duration": row["duration"],
                }
                for _, row in df.iterrows()
            ],
        )

        return {
            "status": "success",
            "rows_inserted": len(df),
            "duplicate_rows_removed": duplicates_removed
        }

    except Exception as e:
        return {"error": str(e)}


# =============================
# 4. SEMANTIC SEARCH ENDPOINT
# =============================
@app.get("/search")
def search(query: str):
    """
    Returns top 5 most relevant videos.
    """
    try:
        results = run_semantic_search(query)
        return {"query": query, "results": results}

    except Exception as e:
        return {"error": str(e)}


# =============================
# 5. SUMMARY ENDPOINT
# =============================
@app.get("/summarize/{video_id}")
def summarize(video_id: str):

    result = summarize_video(video_id)

    if result is None:
        return {"error": "Video ID not found in database"}

    return result


# =============================
# 6. ROOT ENDPOINT
# =============================
@app.get("/")
def home():
    return {"message": "FastAPI VectorDB Server is running successfully!"}
