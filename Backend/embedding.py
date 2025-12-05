import pandas as pd
import re
import isodate
import numpy as np
# You must install this library: pip install sentence-transformers
from sentence_transformers import SentenceTransformer

# --- Configuration ---
# INPUT_CSV_PATH updated to match your error log
INPUT_CSV_PATH = "master_dataset.csv"
OUTPUT_CSV_PATH = "embeddings_updated.csv"

# --- New Configuration for Chunking ---
# Use 256 tokens as the maximum sequence length for all-MiniLM-L6-v2
CHUNK_SIZE = 256
# Overlap by 50 tokens to ensure semantic continuity between chunks
CHUNK_OVERLAP = 50

# --- Helper Functions (from previous step) ---

def clean_text(text):
    """Converts text to lowercase and removes special characters."""
    if pd.isna(text):
        return "" # Return empty string for missing values
    text = str(text)
    text = text.lower()
    text = re.sub(r'[^a-z0-9\\s]', '', text)
    text = re.sub(r'\\s+', ' ', text).strip()
    return text

def convert_iso_duration_to_seconds(iso_duration):
    """Converts ISO 8601 duration (e.g., PT1M30S) to total seconds."""
    if pd.isna(iso_duration):
        return np.nan
    try:
        # Check for the 'duration_seconds' column from the previous cleaning step
        # If it's already a number, just return it.
        if isinstance(iso_duration, (int, float)):
             return iso_duration
        duration_obj = isodate.parse_duration(iso_duration)
        return duration_obj.total_seconds()
    except Exception:
        return np.nan

# -----------------------------------------------------------------
# ⬇️ NEW FUNCTION: Chunking and Embedding with Overlap ⬇️
# -----------------------------------------------------------------

def get_document_embedding(text, model, chunk_size, chunk_overlap):
    """
    Splits long text into overlapping token-aware chunks, embeds them,
    and aggregates the chunk embeddings by taking the mean (Mean Pooling).
    This prevents truncation loss for documents longer than the model's limit.
    """
    # Return a zero vector for empty/missing text
    if pd.isna(text) or text == "":
        return np.zeros(model.get_sentence_embedding_dimension()).tolist()

    # 1. Tokenize the text to get token IDs
    # We use the model's tokenizer for token-aware chunking
    tokens = model.tokenizer.encode(text, add_special_tokens=False)

    # 2. Create overlapping chunks of token IDs
    chunks_of_tokens = []
    # Slide the window by (chunk_size - chunk_overlap)
    stride = chunk_size - chunk_overlap
    for i in range(0, len(tokens), stride):
        chunk = tokens[i : i + chunk_size]
        chunks_of_tokens.append(chunk)

    # 3. Convert token ID chunks back to text strings for embedding
    # This correctly handles subword tokenization by decoding the chunks back to text.
    chunks_of_text = [model.tokenizer.decode(chunk) for chunk in chunks_of_tokens]

    if not chunks_of_text:
        return np.zeros(model.get_sentence_embedding_dimension()).tolist()

    # 4. Generate embeddings for all chunks
    # We use convert_to_numpy for fast aggregation
    chunk_embeddings = model.encode(chunks_of_text, convert_to_numpy=True, show_progress_bar=False)

    # 5. Aggregate embeddings (Mean Pooling)
    # The final document embedding is the average of all chunk embeddings
    document_embedding = np.mean(chunk_embeddings, axis=0)

    # Return the aggregated embedding as a list
    return document_embedding.tolist()

# -----------------------------------------------------------------
# --- Main Logic ---
# -----------------------------------------------------------------

# 1. Load and Clean Data
# ... (rest of your existing code for loading and cleaning) ...
df = pd.read_csv(INPUT_CSV_PATH)
duration_col = 'duration' # Assuming this is the ISO duration column name
if duration_col in df.columns and 'duration_seconds' not in df.columns:
    df['duration_seconds'] = df[duration_col].apply(convert_iso_duration_to_seconds)

# 2. Combine Title and Transcript
print("Combining Title and Transcript for embedding...")

# -----------------------------------------------------------------
# ⬇️ FIX 2: Changed 'Title' to 'video_title' here ⬇️
# -----------------------------------------------------------------
df['combined_text'] = df['video_title'] + ' ' + df['transcript']

# 3. Generate Embeddings
print("Loading embedding model (this may take a moment)...")
try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    print(f"❌ Could not load SentenceTransformer model. Make sure you have installed it.")
    print("Install it with: pip install sentence-transformers")
    print(f"Error: {e}")
    exit()

# -----------------------------------------------------------------
# ⬇️ FIX 3: Replaced direct model.encode() with .apply() using the new chunking function ⬇️
# -----------------------------------------------------------------

print(f"Generating embeddings with chunking (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})... (this will take longer)")

# Apply the new function row-wise to get the aggregated document embedding
df['embeddings'] = df['combined_text'].apply(
    lambda x: get_document_embedding(x, model, CHUNK_SIZE, CHUNK_OVERLAP)
)

# 4. Save Embeddings to DataFrame
print("Adding embeddings to DataFrame...")
# Convert the list of floats (the embedding) into a string for CSV storage
df['embeddings'] = [str(emb) for emb in df['embeddings'].tolist()]

# 5. Save the final DataFrame
df = df.drop(columns=['combined_text'])
df.to_csv(OUTPUT_CSV_PATH, index=False, encoding='utf-8')

print("\\n✅ Embedding generation complete and saved to:", OUTPUT_CSV_PATH)