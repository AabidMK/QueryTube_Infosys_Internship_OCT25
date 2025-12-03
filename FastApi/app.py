from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import pandas as pd
import numpy as np
import faiss
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
import os
from pathlib import Path

app = FastAPI(title="YouTube Vector Search API")

# Serve static files
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/")
async def root():
    return FileResponse(str(static_dir / "index.html"))

# ============================================================
# 1️⃣ Global Variables
# ============================================================
INDEX_PATH = "models/faiss_index.bin"
META_PATH = "models/metadata.pkl"
TFIDF_PATH = "models/tfidf.pkl"
SVD_PATH = "models/svd.pkl"
DATA_PATH = "models/full_data.pkl"

index = None
metadata = None
tfidf_vectorizer = None
svd_model = None
full_data = None

os.makedirs("models", exist_ok=True)

# ============================================================
# Summarization Helper
# ============================================================
def generate_summary(text, max_length=150):
    """Generate a simple extractive summary from text"""
    if not text or pd.isna(text):
        return "No summary available"
    
    text = str(text).strip()
    if len(text) <= max_length:
        return text
    
    # Simple extractive summary: take first sentences
    sentences = text.split('. ')
    summary = ""
    for sent in sentences:
        if len(summary) + len(sent) <= max_length:
            summary += sent + ". "
        else:
            break
    
    return summary.strip() if summary else text[:max_length] + "..."


# ============================================================
# 2️⃣ Helper Functions
# ============================================================
def parse_embedding(emb_str):
    try:
        return np.array(eval(emb_str), dtype="float32")
    except Exception:
        emb_str = emb_str.strip("[]")
        return np.array([float(x) for x in emb_str.split(",")], dtype="float32")


def build_faiss_index(df):
    df["text_embedding"] = df["text_embedding"].apply(parse_embedding)
    embeddings = np.vstack(df["text_embedding"].values).astype("float32")
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    
    # Store additional metadata for summaries
    meta_list = []
    for idx, row in df.iterrows():
        description = row.get("description", "")
        transcript = row.get("transcript", "")
        
        # Prefer description for summary, fallback to transcript
        summary_text = description if description and str(description).strip() else transcript
        summary = generate_summary(summary_text, max_length=150)
        
        meta_list.append({
            "video_id": row.get("video_id"),
            "title": row.get("title"),
            "channel_title": row.get("channel_title"),
            "description": str(description) if description else "",
            "summary": summary
        })
    
    return index, meta_list


# ============================================================
# 3️⃣ API: Upload CSV + Build Vector Index
# ============================================================
@app.post("/ingest")
async def ingest_data(file: UploadFile):
    try:
        df = pd.read_csv(file.file)
        df["transcript"] = df["transcript"].fillna("")
        
        if "text_embedding" not in df.columns:
            return JSONResponse(status_code=400, content={"status": "error", "message": "CSV must contain 'text_embedding' column"})
        
        index, meta = build_faiss_index(df)

        # Save FAISS and metadata
        faiss.write_index(index, INDEX_PATH)
        with open(META_PATH, "wb") as f:
            pickle.dump(meta, f)
        
        # Also save full data for reference
        with open(DATA_PATH, "wb") as f:
            pickle.dump(df, f)

        # Train TF-IDF + SVD
        df["combined_text"] = df["title"].astype(str) + " " + df["transcript"].astype(str)
        tfidf = TfidfVectorizer(stop_words="english", max_features=5000)
        X = tfidf.fit_transform(df["combined_text"])
        svd = TruncatedSVD(n_components=100, random_state=42)
        svd.fit(X)

        # Save models
        with open(TFIDF_PATH, "wb") as f:
            pickle.dump(tfidf, f)
        with open(SVD_PATH, "wb") as f:
            pickle.dump(svd, f)

        return {"status": "success", "message": f"Data ingested successfully! Processed {len(df)} videos.", "records": len(df)}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


# ============================================================
# 4️⃣ API: Search Query
# ============================================================
@app.get("/search")
async def search_videos(query: str, k: int = 5):
    global index, metadata, tfidf_vectorizer, svd_model

    if not all([os.path.exists(INDEX_PATH), os.path.exists(META_PATH)]):
        return JSONResponse(status_code=400, content={"error": "No FAISS index found. Please ingest data first."})

    if index is None:
        index = faiss.read_index(INDEX_PATH)
        with open(META_PATH, "rb") as f:
            metadata = pickle.load(f)
        with open(TFIDF_PATH, "rb") as f:
            tfidf_vectorizer = pickle.load(f)
        with open(SVD_PATH, "rb") as f:
            svd_model = pickle.load(f)

    # Encode query
    query_tfidf = tfidf_vectorizer.transform([query])
    query_emb = svd_model.transform(query_tfidf).astype("float32")

    distances, indices = index.search(query_emb, k)
    scores = 1 / (1 + distances[0])

    results = []
    for rank, i in enumerate(indices[0]):
        data = metadata[i]
        results.append({
            "rank": rank + 1,
            "video_id": data.get("video_id"),
            "title": data.get("title"),
            "channel": data.get("channel_title"),
            "summary": data.get("summary", "No summary available"),
            "description": data.get("description", ""),
            "similarity_score": round(float(scores[rank]), 4)
        })

    return {"query": query, "results": results}
