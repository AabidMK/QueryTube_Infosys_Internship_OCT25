# YouTube Vector Search Engine

This project contains a **FastAPI backend** and a **Streamlit frontend**
for searching YouTube videos using vector embeddings + FAISS.

------------------------------------------------------------------------

## 🚀 Features

-   Upload CSV containing video details + embeddings\
-   Build FAISS index automatically\
-   Perform semantic search with TF‑IDF + SVD\
-   Streamlit UI for uploading and searching\
-   Instant similarity‑based results\
-   Per‑video transcript summarization\
-   Embedded YouTube video preview

------------------------------------------------------------------------

## 📂 Folder Structure

    TASK 9 - FASTAPI, UI MODEL/
    │── backend/
    │   ├── main.py            # FastAPI server
    │   ├── models/            # Saved FAISS index & models
    │
    │── frontend/
    │   ├── app.py             # Streamlit UI
    │
    │── youtube_details_with__embeddings.csv
    │── README.md

------------------------------------------------------------------------

## ⚙️ Backend Setup (FastAPI)

### 1️⃣ Create a virtual environment

    python -m venv venv

### 2️⃣ Activate it

Windows:

    venv\Scriptsctivate

### 3️⃣ Install dependencies

    pip install fastapi uvicorn pandas numpy faiss-cpu scikit-learn python-multipart

### 4️⃣ Run backend

    uvicorn main:app --reload

Backend runs at:

    http://127.0.0.1:8000

------------------------------------------------------------------------

## 🖥️ Frontend Setup (Streamlit)

### 1️⃣ Install dependencies

    pip install streamlit requests pandas

### 2️⃣ Run Streamlit app

    streamlit run app.py

------------------------------------------------------------------------

## 📤 CSV Requirements

Your CSV must contain:

  Column Name      Description
  ---------------- -------------------------------
  video_id         YouTube video ID
  title            Video title
  channel_title    Channel name
  transcript       Video transcript
  text_embedding   100‑dim embedding string list

------------------------------------------------------------------------

## 🔍 Search API

### Example:

    GET /search?query=machine learning&k=5

Returns top‑K most similar videos.

------------------------------------------------------------------------

## 🧪 Testing

After backend starts, open:

    http://127.0.0.1:8000/docs

Swagger UI will be available for testing.

------------------------------------------------------------------------

## 📝 About

YouTube Vector Search --- FastAPI + Streamlit Demo Project.
