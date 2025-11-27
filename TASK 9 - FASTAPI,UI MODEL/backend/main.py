
from fastapi import FastAPI, UploadFile
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np
import faiss
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
import os
import json

app = FastAPI(title="YouTube Vector Search API")

# ================================================
# FILE PATHS
# ================================================
INDEX_PATH = "models/faiss_index.bin"
META_PATH = "models/metadata.pkl"
TFIDF_PATH = "models/tfidf.pkl"
SVD_PATH = "models/svd.pkl"

index = None
metadata = None
tfidf_vectorizer = None
svd_model = None

os.makedirs("models", exist_ok=True)

# ================================================
# Parse embedding from CSV
# ================================================
def parse_embedding(emb_str):
    if pd.isna(emb_str):
        return None
    try:
        return np.array(json.loads(emb_str), dtype="float32")
    except:
        emb_str = emb_str.strip("[]")
        return np.array([float(x) for x in emb_str.split(",")], dtype="float32")

# ================================================
# FIX EMBEDDING SIZE
# ================================================
def fix_embedding_size(embeddings, target_dim=100):
    fixed = []
    for emb in embeddings:
        if emb is None:
            emb = np.zeros(target_dim)
        if len(emb) < target_dim:
            emb = np.pad(emb, (0, target_dim - len(emb)))
        if len(emb) > target_dim:
            emb = emb[:target_dim]
        fixed.append(emb)
    return np.array(fixed).astype("float32")

# ================================================
# BUILD FAISS INDEX
# ================================================
def build_faiss_index(df):
    df["parsed_emb"] = df["text_embedding"].apply(parse_embedding)

    embeddings = fix_embedding_size(df["parsed_emb"].tolist(), target_dim=100)

    index = faiss.IndexFlatL2(100)
    index.add(embeddings)

    meta = df[["video_id", "title", "channel_title", "transcript"]].to_dict(orient="records")
    return index, meta

# ================================================
# INGEST CSV
# ================================================
@app.post("/ingest")
async def ingest_data(file: UploadFile):
    try:
        df = pd.read_csv(file.file)
        df["transcript"] = df["transcript"].fillna("")

        index, meta = build_faiss_index(df)

        faiss.write_index(index, INDEX_PATH)
        with open(META_PATH, "wb") as f:
            pickle.dump(meta, f)

        df["combined_text"] = df["title"].astype(str) + " " + df["transcript"].astype(str)

        vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
        X = vectorizer.fit_transform(df["combined_text"])

        svd = TruncatedSVD(n_components=100)
        svd.fit(X)

        with open(TFIDF_PATH, "wb") as f:
            pickle.dump(vectorizer, f)
        with open(SVD_PATH, "wb") as f:
            pickle.dump(svd, f)

        return {"message": "Data ingested successfully", "records": len(df)}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# ================================================
# SIMPLE SUMMARY GENERATOR
# ================================================
def create_summary(top_items):
    try:
        extracted = [item["title"] for item in top_items]
        summary = (
            "Top matched videos:\n- " +
            "\n- ".join(extracted[:5])
        )
        return summary
    except:
        return "Summary could not be generated."

# ================================================
# SEARCH
# ================================================
@app.get("/search")
async def search_videos(query: str, k: int = 5):
    global index, metadata, tfidf_vectorizer, svd_model

    if not os.path.exists(INDEX_PATH):
        return {"error": "Please upload CSV first using /ingest"}

    if index is None:
        index = faiss.read_index(INDEX_PATH)
        metadata = pickle.load(open(META_PATH, "rb"))
        tfidf_vectorizer = pickle.load(open(TFIDF_PATH, "rb"))
        svd_model = pickle.load(open(SVD_PATH, "rb"))

    q_tfidf = tfidf_vectorizer.transform([query])
    q_emb = svd_model.transform(q_tfidf).astype("float32")

    distances, ids = index.search(q_emb, k)
    scores = 1 / (1 + distances[0])

    results = []
    for rank, idx in enumerate(ids[0]):
        results.append({
            "rank": rank + 1,
            "video_id": metadata[idx]["video_id"],
            "title": metadata[idx]["title"],
            "channel": metadata[idx]["channel_title"],
            "transcript": metadata[idx]["transcript"],
            "similarity_score": float(scores[rank])
        })

    summary_text = create_summary(results)

    return {
        "query": query,
        "summary": summary_text,
        "results": results
    }