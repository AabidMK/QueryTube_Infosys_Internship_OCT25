from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer
import numpy as np
import pandas as pd

# ------------------ CONFIG ------------------ #
local_model_path = r"C:\Users\yadla\OneDrive\Desktop\Query_Tube ai\e5-large-v2"
max_tokens = 510
overlap_tokens = 50

# ------------------ LOAD MODELS ------------------ #
print("📦 Loading model and tokenizer...")
model = SentenceTransformer(local_model_path)
tokenizer = AutoTokenizer.from_pretrained(local_model_path)

# ------------------ CHUNKING FUNCTION ------------------ #
def chunk_text(text, max_tokens=max_tokens, overlap=overlap_tokens):
    if not isinstance(text, str) or text.strip() == "":
        return []
    tokens = tokenizer(text, truncation=False)["input_ids"]
    chunks = []
    start = 0
    while start < len(tokens):
        end = start + max_tokens
        chunk = tokenizer.decode(tokens[start:end], skip_special_tokens=True)
        chunks.append(chunk)
        start += max_tokens - overlap
    return chunks

# ------------------ EMBEDDING FUNCTION ------------------ #
def get_text_embedding(text):
    chunks = chunk_text(text)
    if not chunks:
        return np.zeros(model.get_sentence_embedding_dimension())
    chunk_embeddings = model.encode(chunks, convert_to_numpy=True, normalize_embeddings=True)
    return np.mean(chunk_embeddings, axis=0)

# ------------------ MAIN EXECUTION ------------------ #
print("📂 Reading dataset...")
df = pd.read_csv(r"C:\Users\yadla\OneDrive\Desktop\Query_Tube ai\master_dataset_cleaned.csv")

print("🧩 Combining text columns...")
if "transcript" in df.columns:
    df["combined_text"] = (df["title"].fillna("") + " " + df["transcript"].fillna("")).str.strip()
elif "description" in df.columns:
    df["combined_text"] = (df["title"].fillna("") + " " + df["description"].fillna("")).str.strip()
elif "text" in df.columns:
    df["combined_text"] = (df["title"].fillna("") + " " + df["text"].fillna("")).str.strip()
else:
    df["combined_text"] = df["title"].fillna("").str.strip()

print("⚙️ Generating embeddings (this may take time)...")
df["embedding"] = df["combined_text"].apply(get_text_embedding)
df["embedding"] = df["embedding"].apply(lambda x: x.tolist())

output_path = r"C:\Users\yadla\OneDrive\Desktop\Query_Tube ai\dataset_with_embeddings_final.csv"
df.to_csv(output_path, index=False)

print(f"✅ Embeddings generated and saved successfully at: {output_path}")
