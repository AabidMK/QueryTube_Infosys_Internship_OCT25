import os
import logging
from typing import Optional, Dict, Any, List
import re
from urllib.parse import urlparse, parse_qs

from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel

import pandas as pd
import requests

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

import semantics
import video_summarizer

# ---------------------------------------------------
# Logging
# ---------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------
# Config
# ---------------------------------------------------
CHROMA_DIR = "chroma_store"
COLLECTION_NAME = "video_transcripts"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# ---------------------------------------------------
# YouTube API Config (READ FROM ENVIRONMENT)
# ---------------------------------------------------
# FIX: Read API Key from environment variable YOUTUBE_API_KEY
# YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_API_KEY = "AIzaSyC8rzB6dGJrjF-SVmcRD27c0-NojgHO4A0"
YT_VIDEO_ENDPOINT = "https://www.googleapis.com/youtube/v3/videos"
YT_COMMENTS_ENDPOINT = "https://www.googleapis.com/youtube/v3/commentThreads"

# ---------------------------------------------------
# Initialize Chroma 
# ---------------------------------------------------
try:
    CHROMA_CLIENT = chromadb.Client(Settings(
        is_persistent=True,
        persist_directory=CHROMA_DIR
    ))

    EMBEDDING_FN = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBED_MODEL,
        device="cpu"
    )

    logger.info("Chroma initialized successfully.")

except Exception as e:
    logger.exception("Chroma initialization failed: %s", e)
    CHROMA_CLIENT = None
    EMBEDDING_FN = None


# ---------------------------------------------------
# FastAPI App
# ---------------------------------------------------
app = FastAPI(title="QueryTube Vector Backend")

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------
# Models
# ---------------------------------------------------
class IngestBody(BaseModel):
    video_id: str
    title: str
    content: str
    channel_title: Optional[str] = None


class QueryBody(BaseModel):
    query: str
    top_k: int = 5


# ---------------------------------------------------
# Helpers
# ---------------------------------------------------
def get_collection():
    if CHROMA_CLIENT is None:
        raise RuntimeError("Chroma not initialized")

    return CHROMA_CLIENT.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=EMBEDDING_FN
    )

def _check_youtube_key():
    """Raises exception if API key is not set."""
    if not YOUTUBE_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="YouTube API Key not configured. Please set the YOUTUBE_API_KEY environment variable."
        )

# YouTube ID regex helper
YT_ID_RE = re.compile(r"(?:(?:v=)|(?:/embed/)|(?:/v/)|(?:youtu\.be/))([A-Za-z0-9_-]{11})")

def extract_youtube_id(value: str) -> str:
    """Extract an 11-char YouTube id if possible from a URL or raw id."""
    if not value or not isinstance(value, str):
        return ""
    v = value.strip()
    if len(v) == 11 and re.fullmatch(r"[A-Za-z0-9_-]{11}", v):
        return v
    try:
        parsed = urlparse(v)
        if parsed.hostname and "youtube" in parsed.hostname:
            qs = parse_qs(parsed.query)
            if "v" in qs:
                cand = qs["v"][0]
                if len(cand) == 11:
                    return cand
        m = YT_ID_RE.search(v)
        if m:
            return m.group(1)
    except Exception:
        pass
    return ""
def _check_youtube_key():
    """Raises exception if API key is not set."""
    if not YOUTUBE_API_KEY or YOUTUBE_API_KEY == "YOUR_API_KEY_HERE":
        raise HTTPException(
            status_code=503,
            detail="YouTube API Key not configured. Please set the YOUTUBE_API_KEY environment variable."
        )
# ---------------------------------------------------
# Ingest Single Document
# ---------------------------------------------------
@app.post("/ingest")
def ingest_doc(body: IngestBody):
    try:
        col = get_collection()
        metadata = {"title": body.title, "video_id": body.video_id}

        if body.channel_title:
            metadata["channel_title"] = body.channel_title

        col.add(
            ids=[body.video_id],
            documents=[body.content],
            metadatas=[metadata]
        )

        return {"message": "Document ingested", "id": body.video_id}

    except Exception as e:
        logger.exception("Ingest error: %s", e)
        raise HTTPException(500, f"Ingestion failed: {e}")


# ---------------------------------------------------
# Upload CSV
# ---------------------------------------------------
@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    try:
        df = pd.read_csv(file.file)
        col = get_collection()

        ingested_ids = []
        for _, row in df.iterrows():
            raw_vid = str(row.get("video_id", "")).strip()
            vid = extract_youtube_id(raw_vid) or raw_vid  
            title = row.get("video_title", row.get("title", "")) or ""
            content = row.get("transcript", row.get("content", "")) or ""
            channel = row.get("channel_title", "") or ""

            if not vid or not content:
                continue

            meta = {"video_id": vid, "title": title, "channel_title": channel}

            col.add(
                ids=[vid],
                documents=[content],
                metadatas=[meta]
            )

            ingested_ids.append(vid)

        return {"message": "CSV ingestion complete", "count": len(ingested_ids), "video_ids": ingested_ids}

    except Exception as e:
        logger.exception("CSV ingest failed: %s", e)
        raise HTTPException(500, "CSV ingestion failed")

# ---------------------------------------------------
# Clear Collection
# ---------------------------------------------------
@app.delete("/clear-collection")
def clear_collection():
    """Deletes all data in the video_transcripts collection."""
    if CHROMA_CLIENT is None:
        raise HTTPException(503, "Chroma client is not initialized.")
    
    try:
        CHROMA_CLIENT.delete_collection(name=COLLECTION_NAME)
        logger.info(f"Collection '{COLLECTION_NAME}' deleted successfully.")

        col = get_collection() 
        logger.info(f"Collection '{COLLECTION_NAME}' re-created with {col.count()} documents.")
        
        return {
            "message": f"ChromaDB collection '{COLLECTION_NAME}' cleared and re-created.",
            "new_count": col.count()
        }

    except Exception as e:
        logger.exception("Failed to clear Chroma collection: %s", e)
        raise HTTPException(500, f"Failed to clear collection: {e}")


# ---------------------------------------------------
# Query (Semantic Search)
# ---------------------------------------------------
@app.post("/query")
def query_videos(body: QueryBody):
    try:
        results = semantics.semantic_search(body.query, top_k=body.top_k)
        return {"results": results}
    except Exception as e:
        logger.exception("Query failed: %s", e)
        raise HTTPException(500, f"Query error: {e}")


# ---------------------------------------------------
# Summarize Video (calls video_summarizer)
# ---------------------------------------------------
@app.get("/summarize/{video_id}")
def summarize_video(video_id: str, use_gemini: bool = False):
    try:
        summary = video_summarizer.summarize_video_by_id(video_id, use_gemini=use_gemini)
        if summary is None:
            raise HTTPException(404, "Video not found or no transcript")

        return {"video_id": video_id, "summary": summary}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Summarization error: %s", e)
        raise HTTPException(500, f"Summarization failed: {e}")


# ---------------------------------------------------
# YouTube Metadata (Likes, Views, Comments)
# ---------------------------------------------------
# ingestion_api.py (Updated youtube_meta function)
# ---------------------------------------------------
# YouTube Metadata (Likes, Views, Comments)
# ---------------------------------------------------
@app.get("/youtube/meta/{video_id}")
def youtube_meta(video_id: str):
    _check_youtube_key() # Check for key before making the call
    try:
        params = {
            "id": video_id,
            "part": "snippet,statistics",
            "key": YOUTUBE_API_KEY,
        }
        r = requests.get(YT_VIDEO_ENDPOINT, params=params)
        r.raise_for_status() # Raise an exception for 4xx/5xx HTTP errors
        
        response_json = r.json()

        if "error" in response_json:
            # Log the specific YouTube API error
            error_msg = response_json['error']['message']
            logger.error(f"YouTube Meta API Error for {video_id}: {error_msg}")
            raise HTTPException(500, f"YouTube API error: {error_msg}")

        if "items" not in response_json or len(response_json["items"]) == 0:
            return {"error": "Video not found or details private"}

        item = response_json["items"][0]
        # ... (the rest of the function remains the same)
        
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})

        return {
            "title": snippet.get("title"),
            "channel": snippet.get("channelTitle"),
            "views": stats.get("viewCount"),
            "likes": stats.get("likeCount"),
            "commentCount": stats.get("commentCount")
        }

    except requests.exceptions.HTTPError as he:
        # Log the raw HTTP error (e.g., 403 Forbidden)
        logger.error(f"HTTP Error fetching YouTube metadata for {video_id}: {he}")
        raise HTTPException(500, f"HTTP Error fetching YouTube metadata: {he}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("YouTube meta fetch error: %s", e)
        raise HTTPException(500, "Failed to fetch YouTube metadata")
# ---------------------------------------------------
# YouTube Comments
# ---------------------------------------------------
@app.get("/youtube/comments/{video_id}")
def youtube_comments(video_id: str):
    _check_youtube_key() # Check for key before making the call
    try:
        params = {
            "videoId": video_id,
            "part": "snippet",
            "key": YOUTUBE_API_KEY,
            "maxResults": 20,
            "order": "relevance"
        }
        r = requests.get(YT_COMMENTS_ENDPOINT, params=params).json()

        comments = []
        for item in r.get("items", []):
            top = item["snippet"]["topLevelComment"]["snippet"]
            comments.append({
                "author": top.get("authorDisplayName"),
                "text": top.get("textDisplay"),
                "likes": top.get("likeCount"),
                "published": top.get("publishedAt")
            })

        return {"comments": comments}

    except Exception as e:
        logger.exception("YouTube comment fetch error: %s", e)
        raise HTTPException(500, "Failed to fetch YouTube comments")


# ---------------------------------------------------
# Status
# ---------------------------------------------------
@app.get("/status")
def status():
    ok = CHROMA_CLIENT is not None
    return {
        "chroma_ok": ok,
        "collection": COLLECTION_NAME,
        "model": EMBED_MODEL,
        "persistent_dir": CHROMA_DIR
    }