import pandas as pd
import chromadb
import ast
import os

# --- Configuration ---
INPUT_CSV_PATH = "embeddings_updated.csv"
COLLECTION_NAME = "video_transcripts"
# The embedding model used for generation
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2" 

# --- Data Preparation Functions ---

def load_data_and_prepare_for_chroma(file_path):
    """
    Loads the CSV, converts the embedding strings to lists of floats,
    and structures the data for ChromaDB.
    """
    if not os.path.exists(file_path):
        print(f"❌ Error: Input file not found at {file_path}")
        print("Please run the 'embedding.py' script first to generate this file.")
        return None, None, None, None

    print(f"Loading data from {file_path}...")
    df = pd.read_csv(file_path)

    # 1. Convert the string representation of the embedding list back into a Python list
    df['embeddings'] = df['embeddings'].apply(ast.literal_eval)

    # 2. Prepare the data components for ChromaDB

    # IDs (must be strings)
    ids = df['video_id'].astype(str).tolist()

    # Embeddings (list of vectors)
    embeddings = df['embeddings'].tolist()

    # Documents (The main text to store and return)
    # The transcript is stored here, which is important for retrieval later
    documents = df['transcript'].fillna("").tolist()

    # Metadatas (Additional data to store)
    metadatas = df.apply(
        lambda row: {
            "title": row.get('video_title', 'N/A'),
            "channel_title": row.get('channel_title', 'N/A'),
            "view_count": row.get('view_count', 0),
            "duration": row.get('duration_seconds', 0),
        },
        axis=1
    ).tolist()

    print(f"Loaded {len(df)} records for upload.")
    return ids, embeddings, documents, metadatas

# --- ChromaDB Upload Logic ---

def upload_to_chroma(ids, embeddings, documents, metadatas):
    """Initializes ChromaDB and adds the data to a collection."""
    print(f"Initializing ChromaDB client and collection '{COLLECTION_NAME}'...")

    # Initialize a persistent client to save the DB to disk
    client = chromadb.PersistentClient(path="./chroma_db")

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"} # Use cosine similarity for retrieval
    )

    # Check the current count to avoid re-uploading all data
    current_count = collection.count()
    print(f"Collection currently has {current_count} documents.")

    if current_count > 0:
        print("Data seems to be uploaded. Skipping insertion.")
        return collection
    
    # Batch insertion
    batch_size = 500
    for i in range(0, len(ids), batch_size):
        print(f"Inserting batch {i//batch_size + 1}...")
        batch_ids = ids[i:i + batch_size]
        batch_embeddings = embeddings[i:i + batch_size]
        batch_documents = documents[i:i + batch_size]
        batch_metadatas = metadatas[i:i + batch_size]

        collection.add(
            ids=batch_ids,
            embeddings=batch_embeddings,
            documents=batch_documents,
            metadatas=batch_metadatas
        )

    print(f"✅ Data upload complete! Total documents in collection: {collection.count()}")
    print("Your vector database is saved in the './chroma_db' folder.")

    return collection

# --- Main Execution ---

if __name__ == "__main__":
    ids, embeddings, documents, metadatas = load_data_and_prepare_for_chroma(INPUT_CSV_PATH)
    
    if ids is not None:
        upload_to_chroma(ids, embeddings, documents, metadatas)