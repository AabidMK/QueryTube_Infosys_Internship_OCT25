import uuid
import logging
import time
import subprocess
from typing import Optional, List

import numpy as np
import pandas as pd
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct


# ----------------------------------------
# CONFIG
# ----------------------------------------
QDRANT_URL = "https://63f7ff1e-6ee2-4835-947c-10c1a734cb1e.eu-central-1-0.aws.cloud.qdrant.io"
QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.t81PYTE-2_MdHFYfYXFd7L7qGrdQVsd7g9f04VusYiQ"
DEFAULT_COLLECTION = "youtube_videos_full_payload"
EMBEDDING_MODEL_NAME = "intfloat/e5-large-v2"

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("api")


# ----------------------------------------
# FASTAPI + CORS
# ----------------------------------------
app = FastAPI(title="YouTube Search + Ingestion")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)


# ----------------------------------------
# QDRANT CLIENT
# ----------------------------------------
qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)


# ----------------------------------------
# EMBEDDING MODEL
# ----------------------------------------
_embedding_model = None

def load_model():
    global _embedding_model
    if _embedding_model is None:
        print("🔄 Loading embedding model…")
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _embedding_model


def embed(text: str):
    model = load_model()
    if not text:
        return np.zeros(model.get_sentence_embedding_dimension(), dtype=np.float32)
    return model.encode([text], convert_to_numpy=True, normalize_embeddings=True)[0]


# ----------------------------------------
# HEALTH
# ----------------------------------------
@app.get("/health")
def health():
    return {"status": "running"}


# ----------------------------------------
# SEARCH
# ----------------------------------------
class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 8


@app.post("/search")
def search(req: SearchRequest):
    try:
        model = load_model()
        q_vec = model.encode(req.query, convert_to_numpy=True, normalize_embeddings=True).tolist()

        results = qdrant.search(
            collection_name=DEFAULT_COLLECTION,
            query_vector=q_vec,
            with_payload=True,
            limit=req.top_k,
        )

        return {"results": [
            {"id": r.id, "score": r.score, "payload": r.payload}
            for r in results
        ]}

    except Exception as e:
        return {"error": str(e)}


# ----------------------------------------
# SUMMARIZE
# ----------------------------------------
@app.post("/summarize")
def summarize(req: dict):

    title = req.get("title", "")
    text = (
        req.get("transcript")
        or req.get("combined_text")
        or req.get("description")
        or ""
    ).strip()

    if not text:
        return {"summary": "No transcript available for summarization."}

    prompt = f"""
Summarize the following video clearly:

Title: {title}

Content:
{text[:6000]}

Write:
### Overview
### Key Points
### Insights
### Simple Explanation
"""

    try:
        result = subprocess.run(
            ["ollama", "run", "llama3.1"],
            input=prompt,
            text=True,
            encoding="utf-8",
            capture_output=True,
        )
        output = result.stdout.strip()
        if not output:
            output = "⚠ No summary generated."
        return {"summary": output}

    except Exception as e:
        return {"summary": f"Error: {e}"}


# ----------------------------------------
# CSV INGESTION — FULLY STABLE VERSION
# ----------------------------------------
@app.post("/ingest_csv")
async def ingest_csv(file: UploadFile = File(...)):

    df = pd.read_csv(file.file)
    total = len(df)
    INSERTED = 0

    BATCH_SIZE = 5          # safest possible
    WAIT_TIME = 2           # Qdrant cloud requirement
    RETRY_LIMIT = 3

    batch = []

    for _, row in df.iterrows():

        payload = row.to_dict()
        combined = f"{payload.get('title','')} {payload.get('description','')} {payload.get('transcript','')}"
        payload["combined_text"] = combined

        vector = embed(combined)

        batch.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload=payload
            )
        )

        # batch full → upload safely
        if len(batch) >= BATCH_SIZE:
            success = False
            retries = RETRY_LIMIT

            while not success and retries > 0:
                try:
                    qdrant.upsert(
                        collection_name=DEFAULT_COLLECTION,
                        points=batch
                    )
                    success = True
                except Exception as e:
                    print("⚠ Batch error:", e)
                    retries -= 1
                    time.sleep(3)

            if not success:
                return {"error": "Failed to insert batch after retries."}

            INSERTED += len(batch)
            batch = []
            time.sleep(WAIT_TIME)

    # final leftover
    if batch:
        qdrant.upsert(collection_name=DEFAULT_COLLECTION, points=batch)
        INSERTED += len(batch)

    return {
        "status": "success",
        "rows_inserted": INSERTED,
        "message": f"Uploaded successfully ({INSERTED}/{total})"
    }
