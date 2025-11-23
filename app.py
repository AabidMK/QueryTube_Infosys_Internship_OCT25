from flask import Flask, request, jsonify, render_template
import numpy as np
import faiss
import pickle
import re
import os
import pandas as pd
import io 
from search import semantic_search
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:5500"}})

# Load FAISS + Metadata 

INDEX_FILE = "final_embeddings.index"
META_FILE = "final_metadata.pkl"
EMBEDDING_DIM = 384 

# Load FAISS index
if os.path.exists(INDEX_FILE):
    index = faiss.read_index(INDEX_FILE)
    print("Loaded existing FAISS index")
else:
    index = faiss.IndexFlatIP(EMBEDDING_DIM) 
    print(f"No index found — created new {EMBEDDING_DIM}-dim index")

# Load metadata
if os.path.exists(META_FILE):
    with open(META_FILE, "rb") as f:
        metadata = pickle.load(f)
    print(f"Loaded {len(metadata)} metadata items")
else:
    metadata = []
    print("No metadata found — starting fresh")



# Clean Embedding

def clean_embedding(embedding):
    """Convert string/list embedding into numpy float32 vector"""
    
    if isinstance(embedding, list):
        try:
            return np.array(embedding, dtype="float32")
        except:
            return None

    if isinstance(embedding, str):
        try:
            cleaned = embedding.replace("\n", " ").replace("\r", " ")
            cleaned = re.sub(r"[\[\]]", "", cleaned)
            cleaned = re.sub(r"\s+", " ", cleaned).strip()
            numbers = [float(x) for x in cleaned.split()]
            return np.array(numbers, dtype="float32")
        except Exception as e:
            print(f"Failed to parse embedding string: {e}")
            return None
    if isinstance(embedding, np.ndarray):
        return embedding.astype("float32")
        
    return None



# API: Upload CSV (Easy ingestion)
@app.route("/upload_csv", methods=["POST"])
def upload_csv():
    global index, metadata

    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    csv_file = request.files["file"]

    if csv_file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not csv_file.filename.endswith('.csv'):
         return jsonify({"error": "File is not a CSV"}), 400

    try:
        data = csv_file.stream.read().decode("utf-8")
        df = pd.read_csv(io.StringIO(data))
    except Exception as e:
        return jsonify({"error": f"Failed to read or parse CSV: {str(e)}"}), 400

    # --- Column Validation ---
    required_cols = ["id", "embedding"]
    if not all(col in df.columns for col in required_cols):
        missing = [col for col in required_cols if col not in df.columns]
        return jsonify({"error": f"CSV is missing required columns: {missing}"}), 400

    added, skipped = 0, 0
    
    existing_ids = {v["id"] for v in metadata}

    print(f"Starting CSV ingestion... Found {len(df)} rows.")

    for _, row in df.iterrows():
        vid = row.get("id")
        if hasattr(vid, 'item'):
             vid = vid.item()
        
        if not vid or pd.isna(vid):
            print("Skipped row with missing ID")
            skipped += 1
            continue
        
        # Check for duplicates using the fast set lookup
        if vid in existing_ids:
            print(f"Duplicate skipped: {vid}")
            skipped += 1
            continue

        # Process embedding
        emb = clean_embedding(row.get("embedding"))
        if emb is None or emb.shape[0] != EMBEDDING_DIM:
            print(f"Invalid embedding for video {vid}. Shape: {emb.shape if emb is not None else 'None'}")
            skipped += 1
            continue

        index.add(np.array([emb], dtype="float32"))
        
        # Add to metadata and update our duplicate-check set
        metadata.append(row.to_dict())
        existing_ids.add(vid) 
        added += 1
        print(f"Added: {vid}")

    # Save everything
    if added > 0:
        print(f"Saving index ({index.ntotal} vectors) and metadata ({len(metadata)} items)...")
        faiss.write_index(index, INDEX_FILE)
        with open(META_FILE, "wb") as f:
            pickle.dump(metadata, f)
        print("Save complete.")
    else:
        print("No new items to save.")

    return jsonify({
        "message": "CSV ingestion complete",
        "added": added,
        "skipped": skipped,
        "total": len(metadata)
    })

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload")
def upload():
    return render_template("upload.html")


@app.route("/search", methods=["POST", "OPTIONS"])
def api_search():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    data = request.get_json()
    query = data.get("query")

    print("Received query:", query)

    results = semantic_search(query,top_k=5)
    return jsonify({"results": results})


@app.route("/generate_summary", methods=["POST"])
def generate_summary():
    from summary import generate_summary_from_video  

    data = request.get_json()
    video_id = data.get("video_id")

    print("Summary request received for:", video_id)

    result = generate_summary_from_video(video_id)

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, port=5000)