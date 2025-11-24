# YouTube Video Similarity Search using FAISS

## 📘 Overview
This project builds a **semantic similarity search engine** for YouTube videos using **FAISS** (Facebook AI Similarity Search).  
It uses precomputed **TF-IDF + SVD embeddings** to index and retrieve videos that are most similar in meaning or content.

The system supports:
- Fast nearest-neighbor retrieval using FAISS.
- Metadata storage for each video (ID, view count, embedding).
- Querying similar videos based on vector similarity.

---

## ⚙️ Workflow

### 1. Load and Parse Data
The script loads video details (including text embeddings) from a CSV file:
```python
csv_path = "youtube_details_with_embeddings.csv"
df = pd.read_csv(csv_path)
```

Since embeddings are stored as text in the CSV, each one is parsed into a NumPy vector:
```python
def parse_embedding(emb_str):
    try:
        return np.array(json.loads(emb_str), dtype="float32")
    except:
        emb_str = emb_str.strip("[]")
        return np.array([float(x) for x in emb_str.split(",")], dtype="float32")

df["embedding"] = df["text_embedding"].apply(parse_embedding)
```

---

### 2. Create the Embedding Matrix
All video embeddings are stacked together for FAISS indexing:
```python
embeddings = np.vstack(df["embedding"].values).astype("float32")
```

---

### 3. Build the FAISS Index
A **FlatL2 index** (brute-force Euclidean distance) is used:
```python
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)
```

You’ll see confirmation once embeddings are added:
```
✅ Added 622 embeddings to FAISS index.
```

---

### 4. Store Metadata
Only essential metadata is saved — video ID, view count, and embedding:
```python
metadata = []
for i, row in df.iterrows():
    metadata.append({
        "video_id": row["video_id"],
        "view_count": row["view_count"],
        "embedding": row["embedding"].tolist()
    })
```

Both the FAISS index and metadata are saved for reuse:
```python
faiss.write_index(index, "youtube_faiss.index")
with open("youtube_metadata.pkl", "wb") as f:
    pickle.dump(metadata, f)
```

Result:
```
💾 Saved FAISS index → 'youtube_faiss.index' and metadata → 'youtube_metadata.pkl'
```

---

## 🔍 Querying the Index
Load the FAISS index and metadata:
```python
index = faiss.read_index("youtube_faiss.index")
with open("youtube_metadata.pkl", "rb") as f:
    metadata = pickle.load(f)
```

Run a similarity search with a query embedding (example: random vector for testing):
```python
query_embedding = np.random.rand(index.d).astype("float32").reshape(1, -1)
k = 5  # top 5 similar videos
distances, indices = index.search(query_embedding, k)
```

Display the top-ranked similar videos:
```python
for rank, i in enumerate(indices[0]):
    print(f"\nRank {rank+1}")
    print("Video ID:", metadata[i]["video_id"])
    print("View Count:", metadata[i]["view_count"])
    print("Distance:", distances[0][rank])
    print("Embedding (first 10 values):", metadata[i]["embedding"][:10])
```

---

### 🧩 Example Output
```
Rank 1
Video ID: 0CbxVWOmnAE
View Count: 15323.0
Distance: 34.641357
Embedding (first 10 values): [0.2198, -0.0488, 0.0582, 0.0319, 0.3511, 0.0105, 0.1520, 0.0265, 0.0429, 0.0333]

Rank 2
Video ID: qh6bSF133-k
View Count: 28596.0
Distance: 34.715332
...
```

---

## 🧠 Use Cases
- Find semantically similar YouTube videos.  
- Recommend related content.  
- Cluster videos by topic.  
- Build search engines for large-scale video datasets.

---

## 🧰 Requirements
Install dependencies:
```bash
pip install pandas numpy faiss-cpu
```

> If using GPU acceleration, install `faiss-gpu` instead of `faiss-cpu`.

---

## 📂 Files Generated
| File | Description |
|------|--------------|
| `youtube_details_with_embeddings.csv` | Input dataset with text embeddings |
| `youtube_faiss.index` | FAISS index storing vector representations |
| `youtube_metadata.pkl` | Metadata mapping each embedding to its video details |

---

## 🧑‍💻 Author
Developed by **M. Shalom Vishal**  
Part of **Infosys Internship Project** on YouTube Video Embedding and Similarity Search.
