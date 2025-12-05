# semantics.py
import os
import logging
from typing import List, Dict, Any

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

# Use the same config keys as in ingestion_api
CHROMA_DIR = os.getenv("CHROMA_DIR", "chroma_store")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "video_transcripts")
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

logger = logging.getLogger(__name__)

# create a client & collection accessor (re-usable)
def _get_chroma_collection():
    # Initialize client consistently with persistence settings
    client = chromadb.Client(Settings(is_persistent=True, persist_directory=CHROMA_DIR))
    emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBED_MODEL,
        device="cpu"
    )
    # get_or_create_collection returns the collection
    col = client.get_or_create_collection(name=COLLECTION_NAME, embedding_function=emb_fn)
    return col

def _distance_to_score(distance):
    # We will use the 1 / (1 + d) approach for a safe, non-negative score mapping.
    try:
        d = float(distance)
        return 1.0 / (1.0 + d)
    except Exception:
        return 0.0

def semantic_search(query: str, top_k: int = 10) -> List[Dict[str, Any]]:
    try:
        col = _get_chroma_collection()
    except Exception as e:
        logger.error("Could not open ChromaDB: %s", e)
        return []

    # Ensure we ask Chroma for enough results to cover top_k after deduplication
    # We ask for a minimum of 100 to ensure enough chunks are returned for deduplication.
    ask_n = max(top_k * 5, 100)  

    try:
        # FIX: Removed 'ids' from the include list.
        res = col.query(
            query_texts=[query],
            n_results=ask_n,
            include=['metadatas', 'documents', 'distances'] 
        )
    except Exception as e:
        logger.error("semantic_search failed: %s", e)
        raise

    # Note: Chroma response is a dict of lists (one list-per-query). 
    ids = res.get("ids", [[]])[0]
    metadatas = res.get("metadatas", [[]])[0]
    docs = res.get("documents", [[]])[0]
    dists = res.get("distances", [[]])[0]

    # Build combined list
    combined = []
    for i, vid in enumerate(ids):
        metadata = metadatas[i] if i < len(metadatas) else {}
        doc = docs[i] if i < len(docs) else ""
        dist = dists[i] if i < len(dists) else None
        score = _distance_to_score(dist) if dist is not None else None
        combined.append({
            "id": vid,
            "score": float(score) if score is not None else 0.0,
            "metadata": metadata or {},
            "document": doc or ""
        })

    # Deduplicate by id, keeping the highest score per id
    best_by_id = {}
    for item in combined:
        vid = item.get("id")
        if not vid:
            continue
        cur = best_by_id.get(vid)
        # Check if current item has a higher score
        if cur is None or item["score"] > cur["score"]:
            best_by_id[vid] = item

    # Convert to list and sort by score desc
    results = sorted(best_by_id.values(), key=lambda x: x["score"], reverse=True)

    # Trim to requested top_k
    return results[:top_k]