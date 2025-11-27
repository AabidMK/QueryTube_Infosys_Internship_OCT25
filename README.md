<<<<<<< HEAD
# 📺 YouTube Semantic Search

Semantic search on YouTube video transcripts using **FastAPI**,
**FAISS**, and **React**.

## 📂 Project Structure

    youtube_semantic_search/
    │
    ├── youtube-backend/
    │   ├── main.py
    │   ├── models/
    │
    ├── youtube-frontend/
    │   ├── src/
    │   ├── public/
    │   ├── package.json
    │   ├── vite.config.js

## 🚀 Features

✔ Upload CSV\
✔ Build FAISS index\
✔ TF‑IDF + SVD embeddings\
✔ FastAPI search API\
✔ Gemini summaries\
✔ React frontend

## 🛠 Backend Setup

``` bash
cd youtube-backend
python -m venv venv
venv\Scripts\activate
pip install fastapi uvicorn faiss-cpu pandas numpy scikit-learn google-genai
uvicorn main:app --reload
```

## 🎨 Frontend Setup

``` bash
cd youtube-frontend
npm install
npm run dev
```

## 🔌 API Endpoints

-   **POST /ingest** -- upload CSV + build index\
-   **GET /search?query=...&k=5** -- semantic search with summary

## 🌐 URLs

Backend → http://localhost:8000\
Frontend → http://localhost:5173
=======
# QueryTube_Infosys_Internship_OCT25
AI_SemanticSearchTube. Building a Semantic Search App with YouTube Data
>>>>>>> eec0331401202c5d71f9ab80c08ac20a77c1a1d7
