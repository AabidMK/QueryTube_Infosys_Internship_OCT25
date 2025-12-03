from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import csv
import re
import chardet
from google import genai
import chromadb

# ---------------- CONFIG ----------------
VECTOR_DB_PATH = "chroma_db"
COLLECTION_NAME = "video_analysis_collection"

os.environ["GEMINI_API_KEY"] = "API_KEY_HERE"  # Replace with your actual Gemini API key
MODEL_NAME = "gemini-2.5-flash"
EMBED_MODEL = "text-embedding-004"

# Define custom embedding function
def embed_function(texts):
    client_gem = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    embeddings = []
    for text in texts:
        embed_res = client_gem.models.embed_content(model=EMBED_MODEL, contents=text)
        embeddings.append(embed_res.embeddings[0].values)
    return embeddings

# ---------------- CHROMA INIT ----------------
try:
    client = chromadb.PersistentClient(path=VECTOR_DB_PATH)
    collection = client.get_collection(name=COLLECTION_NAME)
except:
    client = chromadb.PersistentClient(path=VECTOR_DB_PATH)
    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=embed_function,  
        metadata={"dimension": 384}  
    )

# ---------------- FASTAPI APP ----------------
app = FastAPI(title="YouTube VectorDB + Gemini API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- HELPERS ----------------
def extract_video_id(url: str) -> str:
    if not url:
        return ""
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url) or re.search(r"youtu\.be\/([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else url

def _safe_int_from(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        s = value.strip().replace(',', '').replace('+', '')
        m = re.search(r"(\d+)", s)
        if m:
            return int(m.group(1))
    if isinstance(value, dict):
        for k in ("viewCount", "views", "view_count"):
            if k in value:
                return _safe_int_from(value.get(k))
    return None

def _extract_channel(meta: dict):
    if not meta or not isinstance(meta, dict):
        return None
    keys = ['channel_title', 'channelTitle', 'channel', 'uploader', 'author', 'uploader_name', 'creator', 'publisher']
    for k in keys:
        v = meta.get(k)
        if v and isinstance(v, str) and v.strip():
            return v.strip()
    for k in ('owner', 'ownerChannel', 'owner_name'):
        v = meta.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None

def youtube_thumbnail_url(video_id: str):
    return f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"

def youtube_watch_url(video_id: str):
    return f"https://www.youtube.com/watch?v={video_id}"

# ---------------- MODELS ----------------
class SearchRequest(BaseModel):
    query: str

# ---------------- ROUTES ----------------
@app.get("/")
def home():
    return {"message": "Backend running successfully!"}

# ---------- CSV UPLOAD ----------
@app.post("/upload_csv")
async def upload_csv(file: UploadFile = File(...)):
    try:
        client_gem = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        content = await file.read()
        detected = chardet.detect(content)
        encoding = detected['encoding'] or 'utf-8'

        text_content = None
        for enc in [encoding, 'utf-8', 'windows-1252', 'iso-8859-1', 'latin1']:
            try:
                text_content = content.decode(enc)
                break
            except Exception:
                continue
        if text_content is None:
            text_content = content.decode('utf-8', errors='ignore')

        rows = csv.DictReader(text_content.splitlines())
        added = 0
        for row in rows:
            video_id = extract_video_id(row.get("video_id"))
            transcript = row.get("transcript")
            if not video_id or not transcript:
                continue

            embed_res = client_gem.models.embed_content(model=EMBED_MODEL, contents=transcript)
            embedding = embed_res.embeddings[0].values

            collection.add(
                ids=[video_id],
                documents=[transcript],
                embeddings=[embedding],
                metadatas=[{
                    "title": row.get("title", ""),
                    "channel_title": row.get("channel_title", ""),
                    "view_count": int(row.get("view_count") or 0),
                    "duration": row.get("duration", "")
                }]
            )
            added += 1

        return {"message": "CSV uploaded successfully", "rows_added": added}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------- SEMANTIC SEARCH ----------
@app.post("/search")
def search(req: SearchRequest):
    try:
        query = req.query
        if not query:
            raise HTTPException(status_code=400, detail="Query required")

        # Manually embed the query using the same model
        client_gem = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        embed_res = client_gem.models.embed_content(model=EMBED_MODEL, contents=query)
        query_embedding = embed_res.embeddings[0].values
        
        print(f"Query embedding dimension: {len(query_embedding)}")  # Debug

        # Use query_embeddings instead of query_texts
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=10,
            include=["documents", "metadatas", "distances"]
        )
        response = []

        for i in range(len(results["ids"][0])):
            vid = results["ids"][0][i]
            meta = results["metadatas"][0][i]
            doc = results["documents"][0][i]
            dist = float(results["distances"][0][i])

            title = (meta.get("title", "") or f"Video {vid}").strip()
            channel = _extract_channel(meta) or "Unknown"
            view_count = _safe_int_from(meta.get("view_count"))
            duration = meta.get("duration") or "N/A"

            if isinstance(view_count, (int, float)) and view_count >= 0:
                if view_count >= 1_000_000:
                    views_fmt = f"{view_count / 1_000_000:.1f}M"
                elif view_count >= 1_000:
                    views_fmt = f"{view_count / 1_000:.1f}K"
                else:
                    views_fmt = str(view_count)
            else:
                views_fmt = "N/A"

            response.append({
                "video_id": vid,
                "title": title,
                "channel_title": channel,
                "view_count": views_fmt,
                "duration": duration,
                "thumbnail": youtube_thumbnail_url(vid),
                "youtube_url": youtube_watch_url(vid),
                "score": 1 - dist,
                "transcript_snippet": doc[:300] if doc else ""
            })

        # Top 5 by similarity
        response = sorted(response, key=lambda x: x["score"], reverse=True)[:5]
        return {"results": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------- GET VIDEO BY ID ----------
@app.get("/videos/{video_id}")
def get_video(video_id: str):
    vid = extract_video_id(video_id)
    try:
        res = collection.get(ids=[vid], include=["documents", "metadatas", "embeddings"])
        if not res["ids"]:
            raise HTTPException(status_code=404, detail="Video not found")

        doc = res["documents"][0]
        meta = res["metadatas"][0]

        return {
            "video_id": vid,
            "title": meta.get("title", ""),
            "channel_title": _extract_channel(meta),
            "view_count": meta.get("view_count"),
            "duration": meta.get("duration"),
            "thumbnail": youtube_thumbnail_url(vid),
            "youtube_url": youtube_watch_url(vid),
            "transcript": doc
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------- GENERATE SUMMARY ----------
@app.get("/generate_summary/{video_id}")
def generate_summary(video_id: str):
    vid = extract_video_id(video_id)
    try:
        res = collection.get(ids=[vid], include=["documents", "metadatas"])
        if not res["ids"]:
            raise HTTPException(status_code=404, detail="Video not found")
        transcript = res["documents"][0]
        title = res["metadatas"][0].get("title", "(Untitled)")

        client_gem = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        prompt = f"Summarize this YouTube video in simple language.\nTitle: {title}\nTranscript:\n{transcript}"
        response = client_gem.models.generate_content(model=MODEL_NAME, contents=prompt)

        return {"video_id": vid, "title": title, "summary": response.text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
