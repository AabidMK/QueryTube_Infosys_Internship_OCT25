from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import csv
import re
import chardet
from google import genai
import chromadb
from typing import List, Dict, Any

# ---------------- CONFIG ----------------
# Path where the persistent ChromaDB will store data
VECTOR_DB_PATH = ".\chroma_db"
# Name of the collection in the vector database
COLLECTION_NAME = "YOUR COLLECTION NAME"

# NOTE: The API key is included here for demonstration/runtime environment usage.
# In a real-world scenario, you should load this from environment variables securely.
os.environ["GEMINI_API_KEY"] = "YOUR_API_KEY"  # Replace with your actual Gemini API key
MODEL_NAME = "gemini-2.5-flash"
EMBED_MODEL = "text-embedding-004"

# Define custom embedding function for ChromaDB
def embed_function(texts: List[str]) -> List[List[float]]:
    """
    Generates embeddings for a list of texts using the Gemini API.
    This function is used by ChromaDB internally.
    """
    client_gem = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    embeddings = []
    for text in texts:
        # Calls the embed_content endpoint to get the vector for the text
        embed_res = client_gem.models.embed_content(model=EMBED_MODEL, contents=text)
        # Assuming embed_res.embeddings is a list of embeddings
        embeddings.append(embed_res.embeddings[0].values)
    return embeddings

# ---------------- CHROMA INIT ----------------
# Initialize the persistent ChromaDB client and get/create the collection
try:
    client = chromadb.PersistentClient(path=VECTOR_DB_PATH)
    # Tries to get the existing collection
    collection = client.get_collection(name=COLLECTION_NAME)
    print(f"✅ Loaded existing ChromaDB collection: {COLLECTION_NAME}")
except Exception as e:
    # Creates the collection if it doesn't exist, applying the custom embedding function
    client = chromadb.PersistentClient(path=VECTOR_DB_PATH)
    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=embed_function, 
        # Dimension is set to 384 for text-embedding-004
        metadata={"dimension": 384}  
    )
    print(f"➕ Created new ChromaDB collection: {COLLECTION_NAME}")

# ---------------- FASTAPI APP ----------------
app = FastAPI(title="YouTube VectorDB + Gemini API")

# Configure CORS middleware to allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- HELPERS ----------------
def extract_video_id(url: str) -> str:
    """Extracts the 11-character YouTube video ID from a URL."""
    if not url:
        return ""
    # Regex to match standard 'v=' query param or short 'youtu.be/' format
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url) or re.search(r"youtu\.be\/([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else url

def _safe_int_from(value):
    """Safely converts a value (string, int, float, dict) to an integer, handling common view count formats."""
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
    """Tries to find the channel title from various possible metadata keys."""
    if not meta or not isinstance(meta, dict):
        return None
    keys = ['channel_title', 'channelTitle', 'channel', 'uploader', 'author', 'uploader_name', 'creator', 'publisher']
    for k in keys:
        v = meta.get(k)
        if v and isinstance(v, str) and v.strip():
            return v.strip()
    return None

def youtube_thumbnail_url(video_id: str):
    """Generates the URL for the YouTube video's high-resolution thumbnail."""
    return f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"

def youtube_watch_url(video_id: str):
    """Generates the full YouTube watch URL."""
    return f"https://www.youtube.com/watch?v={video_id}"

def get_transcript_snippet_by_id(video_id: str) -> dict:
    """
    Fetches the video's metadata and a 100-character transcript snippet 
    from the ChromaDB collection based on the video ID.
    """
    vid = extract_video_id(video_id)
    if not vid:
        return {"error": "Invalid or missing video ID"}
    
    try:
        # Fetch document and metadata
        res = collection.get(ids=[vid], include=["documents", "metadatas"])
        
        if not res["ids"]:
            return {"error": "Video not found", "status_code": 404}

        document = res["documents"][0]
        metadata = res["metadatas"][0]
        
        # Snippet logic: first 100 characters + "..."
        transcript_snippet = document[:100] + "..." if document else "N/A"
        
        return {
            "video_id": vid,
            "title": metadata.get("title", ""),
            "channel_title": _extract_channel(metadata),
            "transcript_snippet": transcript_snippet,
            "youtube_url": youtube_watch_url(vid),
        }
            
    except Exception as e:
        print(f"❌ ERROR fetching snippet from ChromaDB for {video_id}: {e}")
        return {"error": f"Internal server error: {str(e)}", "status_code": 500}


# ---------------- MODELS ----------------
class SearchRequest(BaseModel):
    """Pydantic model for the semantic search request body."""
    query: str

# ---------------- ROUTES ----------------
@app.get("/")
def home():
    """Simple health check endpoint."""
    return {"message": "Backend running successfully!"}

# ---------- CSV UPLOAD ----------
@app.post("/upload_csv")
async def upload_csv(file: UploadFile = File(...)):
    """
    Reads a CSV file containing video data (video_id, transcript, metadata)
    and uploads it to ChromaDB, embedding the transcripts first.
    """
    try:
        client_gem = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        content = await file.read()
        
        # Detect encoding and decode content
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

            # Embed the transcript using the Gemini API
            embed_res = client_gem.models.embed_content(model=EMBED_MODEL, contents=transcript)
            embedding = embed_res.embeddings[0].values

            # Add the data to the ChromaDB collection
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
        raise HTTPException(status_code=500, detail=f"Error processing CSV upload: {str(e)}")

# ---------- SEMANTIC SEARCH ----------
@app.post("/search")
def search(req: SearchRequest):
    """
    Performs a semantic search against the vector database using the user's query.
    """
    try:
        query = req.query
        if not query:
            raise HTTPException(status_code=400, detail="Query required")

        # Manually embed the query using the same model as the documents
        client_gem = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        embed_res = client_gem.models.embed_content(model=EMBED_MODEL, contents=query)
        query_embedding = embed_res.embeddings[0].values
        
        # Use query_embeddings for ChromaDB vector search
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=10,
            include=["documents", "metadatas", "distances"]
        )
        response = []

        # Process search results
        for i in range(len(results["ids"][0])):
            vid = results["ids"][0][i]
            meta = results["metadatas"][0][i]
            doc = results["documents"][0][i]
            dist = float(results["distances"][0][i]) # Distance score (lower is better)

            title = (meta.get("title", "") or f"Video {vid}").strip()
            channel = _extract_channel(meta) or "Unknown"
            view_count = _safe_int_from(meta.get("view_count"))
            duration = meta.get("duration") or "N/A"

            # Format view count for display
            if isinstance(view_count, (int, float)) and view_count >= 0:
                if view_count >= 1_000_000:
                    views_fmt = f"{view_count / 1_000_000:.1f}M"
                elif view_count >= 1_000:
                    views_fmt = f"{view_count / 1_000:.1f}K"
                else:
                    views_fmt = str(view_count)
            else:
                views_fmt = "N/A"

            # Score is typically 1 - distance for similarity (higher is better)
            response.append({
                "video_id": vid,
                "title": title,
                "channel_title": channel,
                "view_count": views_fmt,
                "duration": duration,
                "thumbnail": youtube_thumbnail_url(vid),
                "youtube_url": youtube_watch_url(vid),
                "score": 1 - dist,
                "transcript_snippet": doc[:300] + "..." if doc and len(doc) > 300 else doc
            })

        # Sort and return top 5 results
        response = sorted(response, key=lambda x: x["score"], reverse=True)[:5]
        return {"results": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during semantic search: {str(e)}")

# ---------- GET VIDEO BY ID (FULL TRANSCRIPT) ----------
@app.get("/videos/{video_id}")
def get_video(video_id: str):
    """Retrieves all metadata and the full transcript for a given video ID."""
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
        raise HTTPException(status_code=500, detail=f"Error retrieving video: {str(e)}")

# ---------- GET TRANSCRIPT SNIPPET ----------
@app.get("/videos/{video_id}/snippet")
def get_video_snippet(video_id: str):
    """Retrieves only the video's metadata and a 100-character transcript snippet."""
    result = get_transcript_snippet_by_id(video_id)
    
    # Check if the helper function returned an error structure
    if "status_code" in result:
        raise HTTPException(status_code=result["status_code"], detail=result["error"])
        
    return result

# ---------- GENERATE SUMMARY ----------
@app.get("/generate_summary/{video_id}")
def generate_summary(video_id: str):
    """Generates a summary of the video transcript using the Gemini model."""
    vid = extract_video_id(video_id)
    try:
        res = collection.get(ids=[vid], include=["documents", "metadatas"])
        if not res["ids"]:
            raise HTTPException(status_code=404, detail="Video not found")
        
        transcript = res["documents"][0]
        title = res["metadatas"][0].get("title", "(Untitled)")

        client_gem = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        
        # Construct prompt for the large language model
        prompt = f"Summarize this YouTube video in simple language, providing key takeaways and main topics discussed.\nTitle: {title}\nTranscript:\n{transcript}"
        
        # Generate content using the Gemini model
        response = client_gem.models.generate_content(model=MODEL_NAME, contents=prompt)

        return {"video_id": vid, "title": title, "summary": response.text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")
