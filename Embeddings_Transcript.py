import pandas as pd
from sentence_transformers import SentenceTransformer

# --- Load your cleaned dataset ---
df = pd.read_csv("C:\\Users\\yadla\\OneDrive\\Desktop\\Query_Tube ai\\master_dataset_cleaned.csv")

# --- Combine title and description into one text field ---
df["combined_text"] = df["title"].fillna('') + " " + df["description"].fillna('')

# --- Load E5-large-v2 embedding model ---
from sentence_transformers import SentenceTransformer

# Local model path
local_model_path = r"C:\Users\yadla\OneDrive\Desktop\Query_Tube ai\e5-large-v2"

# Load from local folder (no internet required)
model = SentenceTransformer(local_model_path)

# --- Add passage prefix (E5 models expect 'query:' or 'passage:' prefixes) ---
texts = ["passage: " + str(t) for t in df["combined_text"].tolist()]

# --- Generate embeddings ---
embeddings = model.encode(texts, show_progress_bar=True, normalize_embeddings=True)

# --- Add embeddings as a new column ---
df["embedding"] = [emb.tolist() for emb in embeddings]

# --- Save to CSV ---
df.to_csv("master_dataset_with_e5_embeddings.csv", index=False)

print("✅ E5-large-v2 embeddings generated and saved as 'master_dataset_with_e5_trascript_embeddings.csv'")
