# 🚀 QueryTube – AI-Powered YouTube Semantic Search & Video Intelligence Platform

QueryTube is an end-to-end system that transforms YouTube video data into a **searchable, summarizable, and analyzable knowledge base** using semantic embeddings and Google Gemini AI.  
This project includes a **Python backend** for search & summarization and a **React UI** for interactive exploration.

---

## 📌 Key Features

- 🔍 **Semantic Search** using sentence-transformer embeddings  
- 🤖 **AI Video Summaries** powered by Gemini  
- 📝 **Dataset ingestion & embedding-based storage**  
- 🚀 **FastAPI backend** for search + summary routes  
- 🖥️ **React frontend** for smooth user experience  
- 📊 Works with **large embedding CSV files**  
- 📁 Clean modular structure  

---

# 📂 Project Structure

```
SHIVANIUIFINAL/
│
├── projectbackend/                     # Backend core (Python)
│   ├── config.py
│   ├── fastapi_ingest.py
│   ├── semantic_search.py
│   ├── summarizer.py
│   ├── masterdataset_with_embeddings.csv
│   └── .env
│
├── projectfrontend/                     # Frontend (React)
│   └── frontend/
│       ├── src/
│       │   ├── pages/
│       │   │   ├── Home.jsx
│       │   │   ├── Search.jsx
│       │   │   ├── Summary.jsx
│       │   │   └── Upload.jsx
│       │   ├── services/api.js
│       │   ├── lib/utils.js
│       │   ├── App.js
│       │   ├── config.js
│       │   └── index.js
│       ├── public/
│       └── .env
│
└── README.md
```

---

# ⚙️ Backend Overview (`projectbackend/`)

## ✅ Semantic Search (`semantic_search.py`)
- Loads precomputed embeddings  
- Converts query → embedding  
- Computes cosine similarity  
- Returns top matching videos  

### Run:
```bash
python projectbackend/semantic_search.py
```

---

## ✅ AI Summarizer (`summarizer.py`)
- Loads transcript + metadata  
- Sends prompt → Gemini  
- Generates clean multi-section summary  

### Run:
```bash
python projectbackend/summarizer.py
```

---

## ✅ FastAPI Server (`fastapi_ingest.py`)

### Available Routes
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/api/health` | Status check |
| POST | `/api/search` | Semantic search |
| POST | `/api/ingest` | Upload CSV |
| GET | `/api/summary/{video_id}` | AI summary |

### Start API:
```bash
uvicorn fastapi_ingest:app --reload
```

---

# 🧠 Embeddings Dataset

File: `masterdataset_with_embeddings.csv`

Contains:
- Video metadata  
- Cleaned transcript  
- Sentence-transformer embeddings (`all-MiniLM-L6-v2`)  
- IDs for search  

This file powers the semantic search engine.

---

# 🖥️ Frontend Overview (`projectfrontend/frontend/`)

A React app providing:
- Search interface  
- Summary viewer  
- Upload module  
- Clean navigation  

---

## 📄 Pages Overview

### **Home.jsx**
Intro + navigation.

### **Search.jsx**
- Search bar  
- Result list  
- Retrieves `/api/search`  

### **Summary.jsx**
- Displays AI summary  
- Retrieves `/api/summary/{video_id}`  

### **Upload.jsx**
- Uploads CSV datasets  
- Calls `/api/ingest`  

---

## 🌐 API Integration (`services/api.js`)

Handles:
- `searchVideos(query)`  
- `getSummary(videoId)`  
- `uploadDataset(file)`  

Uses base URL from `config.js`.

---

## 🔧 Frontend Environment (`frontend/.env`)
```
REACT_APP_API_URL=http://localhost:8000
```

---

## ▶ Start Frontend
```bash
cd projectfrontend/frontend
npm install
npm start
```

---

# 🔄 Workflow Summary

1️⃣ **Dataset → Embeddings**  
 – Data cleaned, embedded, saved in CSV  

2️⃣ **Semantic Search**  
 – Query embedded → compared to dataset  

3️⃣ **Summarization**  
 – Gemini generates insights + key points  

4️⃣ **UI**  
 – Displays results + summaries  

---

# 🖼️ UI Screenshots

```

```
<img width="1781" height="736" alt="Screenshot 2025-12-05 193020" src="https://github.com/user-attachments/assets/9229aa12-ea15-45c1-b8a3-fb3563515561" />
<img width="1892" height="779" alt="Screensh<img width="1856" height="780" alt="Screenshot 2025-12-05 193200" src="https://github.com/user-attachments/assets/ca04d9f9-ab12-4455-92b0-50e1d7a07f98" />

---

# 📦 Install Dependencies

## Backend:
```bash
pip install fastapi uvicorn pandas numpy sentence-transformers google-generativeai python-dotenv
```

## Frontend:
```bash
npm install
```

---

# 🚀 Run Complete System

### Start Backend
```bash
uvicorn prb.fastapi_ingest:app --reload
```

### Start Frontend
```bash
cd prf/frontend
npm start
```

---

# ✔️ Summary of Features

| Feature | Description |
|--------|-------------|
| 🔍 Semantic Search | Embedding-based |
| 🤖 Gemini Summaries | AI-powered |
| 📤 CSV Upload | Add new datasets |
| 🖥️ React UI | Smooth and modern |
| ⚡ FastAPI Backend | Lightweight and fast |
| 📂 Embedding Storage | CSV-based |


# 📜 License
MIT License © 2025

