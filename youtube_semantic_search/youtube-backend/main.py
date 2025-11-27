# youtube-backend/main.py
from fastapi import FastAPI, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

import pandas as pd
import numpy as np
import faiss
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
import os
import json

# ---------- Gemini Imports ----------
from google import genai
from google.genai.types import Content

app = FastAPI(title="YouTube Vector Search API")

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# ---------- Model file paths ----------
INDEX_PATH = "models/faiss_index.bin"
META_PATH = "models/metadata.pkl"
TFIDF_PATH = "models/tfidf.pkl"
SVD_PATH = "models/svd.pkl"

index = None
metadata = None
tfidf_vectorizer = None
svd_model = None

os.makedirs("models", exist_ok=True)

# ---------- Gemini API Key (Hard-coded here) ----------
GEMINI_API_KEY = "AIzaSyARy_O3SPWBIT3oU2J4Em3MjtZ6NcvZbd0"
# Initialize Gemini
gemini_client = genai.Client(api_key=GEMINI_API_KEY)


# ---------- Helpers ----------
def parse_embedding(emb_str):
    if pd.isna(emb_str):
        return None
    try:
        return np.array(json.loads(emb_str), dtype="float32")
    except Exception:
        s = str(emb_str).strip().strip("[]")
        if not s:
            return None
        return np.array([float(x) for x in s.split(",")], dtype="float32")


def fix_embedding_size(embeddings, target_dim=100):
    fixed = []
    for emb in embeddings:
        if emb is None:
            emb = np.zeros(target_dim, dtype="float32")
        if len(emb) < target_dim:
            emb = np.pad(emb, (0, target_dim - len(emb))).astype("float32")
        if len(emb) > target_dim:
            emb = emb[:target_dim].astype("float32")
        fixed.append(emb)
    return np.array(fixed).astype("float32")


def build_faiss_index(df, emb_dim=100):
    df["parsed_emb"] = df["text_embedding"].apply(parse_embedding)
    embeddings = fix_embedding_size(df["parsed_emb"].tolist(), target_dim=emb_dim)

    idx = faiss.IndexFlatL2(emb_dim)
    idx.add(embeddings)

    meta_cols = [
        "video_id", "title", "channel_title", "transcript",
        "description", "thumbnail", "video_url", "views", "likes"
    ]

    for c in meta_cols:
        if c not in df.columns:
            df[c] = "" if c not in ["views", "likes"] else 0

    meta = df[meta_cols].to_dict(orient="records")
    return idx, meta


# -------------- Gemini Summarizer --------------
def summarize_text(text, max_chars=200):
    try:
        if not text or len(text.strip()) == 0:
            return "No summary available."

        prompt = f"""
        Summarize the following text in under {max_chars} characters.
        Make it short, meaningful, and easy to understand:

        {text}
        """

        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt]
        )
        return response.text.strip()

    except Exception as e:
        return f"Summary unavailable ({str(e)})."


# -------------------- Routes --------------------
@app.post("/ingest")
async def ingest_data(file: UploadFile):
    try:
        df = pd.read_csv(file.file)

        df["transcript"] = df.get("transcript", "").fillna("")
        df["description"] = df.get("description", "").fillna("")
        df["views"] = df.get("views", 0).fillna(0).astype(int)
        df["likes"] = df.get("likes", 0).fillna(0).astype(int)

        index_local, meta = build_faiss_index(df, emb_dim=100)

        faiss.write_index(index_local, INDEX_PATH)
        with open(META_PATH, "wb") as f:
            pickle.dump(meta, f)

        df["combined_text"] = (
            df["title"].astype(str) + " " +
            df["transcript"].astype(str) + " " +
            df["description"].astype(str)
        )

        vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
        X = vectorizer.fit_transform(df["combined_text"])

        svd = TruncatedSVD(n_components=100)
        svd.fit(X)

        pickle.dump(vectorizer, open(TFIDF_PATH, "wb"))
        pickle.dump(svd, open(SVD_PATH, "wb"))

        return {"message": "Data ingested successfully", "records": len(df)}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/search")
async def search_videos(query: str, k: int = 5):
    global index, metadata, tfidf_vectorizer, svd_model

    if not os.path.exists(INDEX_PATH):
        return JSONResponse(
            status_code=400,
            content={"error": "Please upload CSV first using /ingest"}
        )

    if index is None:
        index = faiss.read_index(INDEX_PATH)
        metadata = pickle.load(open(META_PATH, "rb"))
        tfidf_vectorizer = pickle.load(open(TFIDF_PATH, "rb"))
        svd_model = pickle.load(open(SVD_PATH, "rb"))

    q_tfidf = tfidf_vectorizer.transform([query])
    q_emb = svd_model.transform(q_tfidf).astype("float32")

    distances, ids = index.search(q_emb, k)
    distances = distances[0].tolist()
    ids = ids[0].tolist()

    results = []
    for i, idx in enumerate(ids):
        if idx < 0 or idx >= len(metadata):
            continue

        item = metadata[idx]

        summary_input = (
            item.get("description") or
            item.get("transcript") or
            item.get("title")
        )

        summary = summarize_text(summary_input, max_chars=200)

        results.append({
            "rank": int(i + 1),
            "video_id": str(item.get("video_id", "")),
            "title": str(item.get("title", "")),
            "channel": str(item.get("channel_title", "")),
            "transcript": str(item.get("transcript", "")),
            "description": str(item.get("description", "")),
            "thumbnail": str(item.get("thumbnail", "")),
            "video_url": str(item.get("video_url",
                f"https://www.youtube.com/watch?v={item.get('video_id','')}")),
            "views": int(item.get("views", 0)),
            "likes": int(item.get("likes", 0)),
            "summary": summary,
            "similarity_score": float(1 / (1 + distances[i]))
        })

    return {"query": query, "results": results}
