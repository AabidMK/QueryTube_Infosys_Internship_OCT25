# video_summarizer.py

import os
import chromadb
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# Gemini (optional)
try:
    from google import genai
    HAS_GEMINI = True
except Exception:
    genai = None
    HAS_GEMINI = False
    logger.warning("Google GenAI SDK not found. Summaries will use local fallback.")

# Config (Unified with ingestion_api.py)
# FIX: Renamed CHROMA_DB_PATH to CHROMA_DIR for consistency
CHROMA_DIR = os.getenv("CHROMA_DIR", "chroma_store")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "video_transcripts")
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")


# ---------------------------
# DB Helpers
# ---------------------------
def get_collection():
    """Opens the persistent ChromaDB collection."""
    # FIX: Using PersistentClient with the corrected CHROMA_DIR path
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    return client.get_collection(name=COLLECTION_NAME)


def get_transcript_by_id(collection, video_id: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Retrieves transcript + title for a specific video.
    Returns (title, transcript)
    """
    try:
        resp = collection.get(
            ids=[video_id],
            include=['documents', 'metadatas']
        )
    except Exception as e:
        logger.error(f"Error retrieving transcript for ID {video_id}: {e}")
        return None, None

    if not resp.get('ids') or not resp['ids'][0]:
        return None, None
    
    title = resp['metadatas'][0].get('title') if resp['metadatas'] and resp['metadatas'][0] else None
    transcript = resp['documents'][0] if resp['documents'] and resp['documents'][0] else None

    return title, transcript


# ---------------------------
# Summarization Methods
# ---------------------------
def gemini_summary(title: str, transcript: str) -> str:
    """Uses Gemini to summarize the transcript."""
    if not HAS_GEMINI:
        return simple_local_summary(transcript)

    client = genai.Client()
    
    prompt = f"""
You are an expert video summarizer. Your task is to provide a concise, readable, and highly informative summary of the video transcript provided below.
The summary should capture the main points and key takeaways. Do not include any introductory or concluding phrases, just the summary text.

Video Title: {title}

Transcript:
---
{transcript}
---

Write ONLY the summary.
"""

    response = client.models.generate_content(
        model=GEMINI_MODEL_NAME,
        contents=prompt
    )

    return response.text


def simple_local_summary(transcript: str) -> str:
    """Local fallback summarizer — selects longest sentences."""
    import re

    sentences = re.split(r'(?<=[.!?])\s+', transcript.strip())
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

    if not sentences:
        return "(Transcript too short to summarize.)"

    # Select the 5 longest sentences as a simple summary
    chosen = sorted(sentences, key=lambda s: len(s), reverse=True)[:5]
    return ".\n".join([s.rstrip('.') for s in chosen]) + "." # Re-add a final period

# ---------------------------
# Main summarization method
# ---------------------------

def summarize_video_by_id(video_id: str, use_gemini: bool = True) -> Optional[str]:
    """
    Called directly by FastAPI route /summarize/{video_id}.
    Returns summary string or None.
    """
    try:
        collection = get_collection()
    except Exception as e:
        logger.exception("Could not open ChromaDB in summarizer: %s", e)
        return "Error: Could not access video database."

    title, transcript = get_transcript_by_id(collection, video_id)

    if not transcript:
        return None # 404 handled by caller

    if use_gemini and HAS_GEMINI:
        return gemini_summary(title, transcript)
    else:
        return simple_local_summary(transcript)