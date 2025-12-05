# 🎬 QueryTube — YouTube Video Intelligence

### **FastAPI + React Application for Managing YouTube Transcript Embedding Databases**

This project provides a **full-stack application** to manage multiple ChromaDB collections, upload YouTube transcript CSVs, perform semantic search, generate summaries, and manage metadata — all via a React frontend and a FastAPI backend.

The backend uses **ChromaDB** for vector storage and **FastAPI** for API routing.
The frontend (in the `/frontend` directory) is built with **React**.

---

## 📁 Project Structure

```
project-root/
│── app.py                     # FastAPI backend
│── summarize.py               # Transcript tools (fetch + summarize)
│── chroma_db/                 # ChromaDB persistent storage
│── frontend/                  # React front-end app
│── README.md
```

---

# 🚀 Features

### 🧱 Database Management

* Create new ChromaDB collections from CSV uploads
* Upload new data into existing databases
* Delete entire ChromaDB collections
* List all databases and their document counts

### 🔍 Search & Metadata

* Perform semantic search with stored embeddings
* Fetch complete video metadata + transcript
* Smooth interaction with the React UI

### 📝 Transcript Summarization

* Automatically fetch transcript from database
* Summarize using `summarize_text()`

### 🗑 Record Deletion (with Backup)

* Delete specific rows by video ID
* Automatically save deleted data in a backup CSV

---

# 🛠 Requirements

### Backend Dependencies

Install using:

```
pip install fastapi uvicorn chromadb pandas tqdm python-multipart pydantic
```

### Frontend Requirements

```
Node 16+
npm or yarn
React 18+
```

---

# ⚙️ Backend Setup (FastAPI)

### 1. Create & activate virtual environment

```bash
python -m venv venv
source venv/bin/activate     # Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

> If no `requirements.txt` exists, create one containing:

```
fastapi
uvicorn
chromadb
pandas
tqdm
python-multipart
pydantic
```

### 3. Start backend server

```bash
uvicorn app:app --reload
```

Backend will run at:

* **[http://127.0.0.1:8000](http://127.0.0.1:8000)**
* API Docs: **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

---

# 🖥 Frontend Setup (React)

### 1. Install dependencies

```bash
cd frontend
npm install
```

### 2. Start React dev server

```bash
npm start
```

Frontend will run at:

👉 [http://localhost:3000](http://localhost:3000)

---

# 🔗 API Endpoints Overview

## 🧱 Create a new database

```
POST /create_db
```

**Required CSV columns:**

| id | transcript | embedding | title | channel_title | viewCount | duration_seconds |
| -- | ---------- | --------- | ----- | ------------- | --------- | ---------------- |

---

## 📤 Upload into existing database

```
POST /upload_csv
```

---

## 🔍 Perform semantic search

```
GET /search
?collection_name=...
&query=...
```

---

## 📝 Summarize transcript

```
POST /summarize
```

### Body:

```json
{
  "video_id": "abc123",
  "collection_name": "mydatabase"
}
```

Transcript is always fetched from DB.

---

## 🎬 Get metadata for a specific video

```
GET /video_metadata
?collection_name=...
&video_id=...
```

---

## 🗑 Delete records + backup CSV

```
POST /delete_records
```

---

## 🗂 List all databases

```
GET /health
```

---

## ❌ Delete entire database

```
DELETE /delete_db
?collection_name=...
```

---

# 📦 CSV Format

Your uploaded CSV **must include**:

* `id`
* `transcript`
* `embedding` → stringified vector list like `"[0.12, -0.55, ...]"`
* `title`
* `channel_title`
* `viewCount`
* `duration_seconds`

---

# 🧠 Summarization Logic

Backend uses:

```python
summary = summarize_text(transcript)
```

You can implement this using:

* OpenAI API
* Local LLM
* Custom summarizer

---

# 🛡 CORS Configuration

Backend allows:

```
http://localhost:3000
```

Modify inside `app.py` if deploying elsewhere.

---

# 🎯 Deployment Tips

### Backend

* Run FastAPI with Uvicorn/Gunicorn behind Nginx
* Persist the `chroma_db/` folder
* Add environment variables for API keys

### Frontend

```bash
npm run build
```

