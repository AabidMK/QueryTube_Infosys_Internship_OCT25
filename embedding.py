import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import tiktoken
from tqdm import tqdm

df = pd.read_csv("cleaned_master_youtube_data.csv")

df["combined_text"] = df["title"].fillna('') + " " + df["transcript"].fillna('')

tokenizer = tiktoken.get_encoding("cl100k_base")

def count_tokens(text):
    return len(tokenizer.encode(text))

def chunk_text(text, chunk_size=400, overlap=50):
    tokens = tokenizer.encode(text)
    chunks = []
    start = 0
    while start < len(tokens):
        end = start + chunk_size
        chunk = tokens[start:end]
        chunks.append(tokenizer.decode(chunk))
        start += chunk_size - overlap  # move with overlap
    return chunks

# Embedding Model
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

all_embeddings = []

for text in tqdm(df["combined_text"], desc="Generating embeddings"):
    chunks = chunk_text(text)
    chunk_embeddings = model.encode(chunks)
    # Average pooling of chunk embeddings to get one vector per transcript
    avg_embedding = np.mean(chunk_embeddings, axis=0)
    all_embeddings.append(avg_embedding.tolist())

df["embedding"] = all_embeddings

df.to_csv("data_chunked_embeddings.csv", index=False)

print("Chunked embeddings saved successfully!")
