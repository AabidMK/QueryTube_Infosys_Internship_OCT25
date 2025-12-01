# YouTube VectorDB & Semantic Dashboard

A full-stack web application for managing, searching, and summarizing YouTube video transcripts using **FastAPI** backend and **React** frontend. Users can upload CSV datasets, search semantically, fetch video details, and generate video summaries.

---

## Features

- **CSV Upload**: Add YouTube video transcripts with metadata into a Chroma vector database.
- **Fetch Video Details**: Retrieve video metadata and transcript by video ID.
- **Semantic Search**: Search videos based on query similarity.
- **Generate Summary**: Summarize a video transcript using Google Gemini AI.

## Installation

### Backend (FastAPI)
1. Create a virtual environment:

python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows


2. Install dependencies:

pip install -r requirements.txt


3. Set environment variables:

export GEMINI_API_KEY="YOUR_GOOGLE_GEMINI_KEY"      # Linux/Mac
set GEMINI_API_KEY="YOUR_GOOGLE_GEMINI_KEY"         # Windows


4. Run the API server:

uvicorn main:app --reload


The API will be available at http://127.0.0.1:8000

### Frontend (React)


1. Install dependencies:

npm install


2. Start the development server:

npm run dev


Open http://localhost:5173 (or the port shown in terminal)