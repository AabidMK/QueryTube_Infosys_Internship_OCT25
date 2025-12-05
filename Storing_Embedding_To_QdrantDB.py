from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, PointStruct
import numpy as np
import pandas as pd
import uuid

# =============================================================
# 1. Load E5 Model & Tokenizer
# =============================================================
model_name = "intfloat/e5-large-v2"
model = SentenceTransformer(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)


# =============================================================
# 2. Qdrant DB Connection
# =============================================================
qdrant_client = QdrantClient(
    url="https://63f7ff1e-6ee2-4835-947c-10c1a734cb1e.eu-central-1-0.aws.cloud.qdrant.io:6333",
    api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.-jeQEhiuo5KV5Q3Ha-YfUatW13_iR3olPapJNQqIgwk",
    timeout=60
)

collection_name = "youtube_videos_full_payload"


# =============================================================
# 3. Create Collection (1024-dimensional embeddings)
# =============================================================
if not qdrant_client.collection_exists(collection_name):
    qdrant_client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=model.get_sentence_embedding_dimension(),
            distance="Cosine"
        )
    )
    print(f"✅ Created collection: {collection_name}")
else:
    print(f"ℹ️ Collection '{collection_name}' already exists. Adding data...")


# =============================================================
# 4. Chunk Text for Long Transcripts
# =============================================================
def chunk_text(text, max_tokens=510, overlap=50):
    if not isinstance(text, str):
        return []

    tokens = tokenizer(text, truncation=False)["input_ids"]
    chunks, start = [], 0

    while start < len(tokens):
        end = start + max_tokens
        chunk = tokenizer.decode(tokens[start:end], skip_special_tokens=True)
        chunks.append(chunk)
        start += max_tokens - overlap

    return chunks


# =============================================================
# 5. Generate Embedding With Chunk Merging
# =============================================================
def create_embedding(text):
    chunks = chunk_text(text)
    if not chunks:
        return np.zeros(model.get_sentence_embedding_dimension())

    vectors = model.encode(
        chunks,
        convert_to_numpy=True,
        normalize_embeddings=True
    )
    return np.mean(vectors, axis=0)


# =============================================================
# 6. Load Your CSV (ALL 622 rows)
# =============================================================
df = pd.read_csv(r"C:\Users\yadla\OneDrive\Desktop\Query_Tube ai\master_dataset_with_e5_embeddings _final.csv")

print("\n📌 Columns detected in CSV:")
print(list(df.columns))


# =============================================================
# 7. Build Combined Text Column
# =============================================================
TEXT_COLUMNS = ["transcript", "description", "cleaned_transcript"]

text_col = next((c for c in TEXT_COLUMNS if c in df.columns), None)
if not text_col:
    raise ValueError("❌ No transcript/description column found!")

df["combined_text"] = (df["title"].fillna("") + " " + df[text_col].fillna("")).str.strip()
print(f"\n📌 Using '{text_col}' as text source.")


# =============================================================
# 8. Convert NaN → None (Qdrant payload requirement)
# =============================================================
df = df.replace({np.nan: None})


# =============================================================
# 9. Upload All 622 Rows to Qdrant
# =============================================================
BATCH_SIZE = 50
batch = []

print(f"\n🚀 Uploading {len(df)} videos (all columns included)...\n")

for i, row in df.iterrows():

    # --- Generate embedding ---
    emb = create_embedding(row["combined_text"]).astype(np.float16)

    # --- Convert row to payload (ALL COLUMNS) ---
    payload = row.to_dict()

    # --- Add embedding point ---
    point = PointStruct(
        id=str(uuid.uuid4()),
        vector=emb.tolist(),
        payload=payload
    )
    batch.append(point)

    # --- Upload batch ---
    if len(batch) == BATCH_SIZE:
        qdrant_client.upsert(collection_name=collection_name, points=batch)
        print(f"📤 Uploaded batch up to row {i+1}/{len(df)}")
        batch = []

# Upload remaining
if batch:
    qdrant_client.upsert(collection_name=collection_name, points=batch)
    print(f"📤 Uploaded last batch ({len(batch)} points).")

print("\n🎉 SUCCESS! All 622 videos stored in Qdrant with ALL columns!")
