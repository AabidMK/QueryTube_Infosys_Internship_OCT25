# QueryTube_Infosys_Internship_OCT25
AI_SemanticSearchTube. Building a Semantic Search App with YouTube Data
YouTube Semantic SearchTube 🎬
A comprehensive YouTube video search and summarization system that uses semantic search to find relevant videos and AI-powered summarization to generate concise summaries.

🌟 Features
🔍 Semantic Video Search
Search through 615+ YouTube videos using natural language queries

Vector-based similarity search for accurate results

Filter by channel and relevance score

Real-time search with instant results (10 results per query)

Sort by relevance and other filters

🤖 AI-Powered Summarization
Automatic video summarization using Ollama/LLaMA 3.2

Extract key points from video transcripts

Support for both AI and basic summarization methods

Batch summarization for multiple videos

Real-time summarization while searching

📊 Metadata Management
Complete video metadata storage

View count, duration, channel information

Published dates and video tags

Transcript storage and processing

Channel-based filtering

🗄️ Vector Database
ChromaDB for efficient vector storage with 615+ videos

Persistent embeddings for fast retrieval

Scalable architecture for large video collections

Pre-computed embeddings using all-MiniLM-L6-v2 model

🖥️ User Interface
Main Dashboard
The interface includes:

Search Bar: Enter natural language queries to find videos

Filters Panel: Filter results by channel and other criteria

Results Display: Shows 10 results per search, sorted by relevance

Video Metadata: Display title, channel, views, and similarity score

AI Summary: Integrated summarization for each video

Development Environment
https://Screenshot%2520(37).png

Project structure in VS Code:

text
youtube-api-ui/
├── python/                    # Backend files
│   ├── main.py              # FastAPI server
│   ├── video_summarizer.py  # AI summarization
│   └── ...
├── chroma_db/               # Vector database
├── src/                     # React frontend
├── public/                  # Static assets
└── package.json            # Frontend dependencies
🚀 Quick Start
Prerequisites
Python 3.8+

Node.js 16+

Ollama (for AI summarization)

ChromaDB

Git

Installation
Clone and Setup Backend

bash
# Navigate to backend directory
cd youtube-api

# Install Python dependencies
pip install -r requirements.txt

# Install Ollama (for AI summarization)
# Download from https://ollama.ai/
ollama pull llama3.2

# Prepare dataset and embeddings
python yt_embedding.py
python setup_chromadb.py

# Start the backend server
python main.py
Setup Frontend (React)

bash
# Navigate to frontend directory
cd ../youtube-api-ui

# Install Node.js dependencies
npm install

# Start the React development server
npm start
Access the Application

Backend API: http://localhost:8000

Frontend UI: http://localhost:3000

API Documentation: http://localhost:8000/docs

📊 System Architecture
Current Setup Status
text
✅ Backend Status:
   - FastAPI Server: Running on port 8000
   - ChromaDB: Connected with 615 videos
   - Embeddings: Pre-computed using all-MiniLM-L6-v2
   - AI Summarizer: Available (Ollama + LLaMA 3.2)
   - CORS: Enabled for React frontend

✅ Frontend Status:
   - React Application: Running on port 3000
   - Search Interface: Complete
   - Results Display: Implemented
   - Filters: Channel and relevance sorting
   - Integration: Connected to backend API

✅ Database Status:
   - Total Videos: 615
   - Vector Dimensions: 384 (MiniLM-L6-v2)
   - Storage: Persistent at C:\Users\Admin\Desktop\Youtube_db\chroma_db
   - Collection: youtube_videos
🔧 API Integration
Backend-Frontend Communication
javascript
// Example search request from React
const searchVideos = async (query) => {
  const response = await fetch('http://localhost:8000/search/with_summary/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query: query,
      n_results: 10,
      include_summary: true
    })
  });
  return await response.json();
};

// Example video summarization
const summarizeVideo = async (videoId) => {
  const response = await fetch('http://localhost:8000/summarize/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      video_id: videoId,
      use_ai: true,
      save_to_file: false
    })
  });
  return await response.json();
};
🎯 Key Components
1. Search Interface
Natural Language Queries: "science mysteries", "ancient civilizations"

Relevance Sorting: Cosine similarity scoring

Channel Filters: Filter by specific YouTube channels

Real-time Results: Instant search as you type

2. Video Results Display
Similarity Score: Shows how closely each video matches your query

Metadata: Title, channel, views, duration

Content Preview: First 200 characters of transcript/description

AI Summary: 2-3 sentence summary generated on demand

3. AI Summarization
Model: LLaMA 3.2 via Ollama

Context: Uses video title and transcript

Output: Concise 2-3 sentence summaries

Fallback: Basic extractive summarization if AI unavailable

📈 Performance Metrics
Search Performance
Query Response Time: < 500ms for semantic search

Vector Similarity: Cosine similarity scoring

Result Accuracy: Top 10 most relevant videos

Scaling: Supports 615+ videos with room for expansion

Summarization Performance
AI Summary Time: 2-3 seconds per video

Basic Summary Time: < 500ms

Batch Processing: Parallel summarization for multiple videos

Quality: Human-readable, informative summaries

🛠️ Development Workflow
Backend Development
bash
# Test backend endpoints
curl -X POST "http://localhost:8000/search/" \
  -H "Content-Type: application/json" \
  -d '{"query": "test query", "n_results": 5}'

# Check system health
curl http://localhost:8000/health

# Test summarization
curl -X POST "http://localhost:8000/summarize/" \
  -H "Content-Type: application/json" \
  -d '{"video_id": "t8txtQkhMcY", "use_ai": true}'
Frontend Development
bash
# Start development server
npm start

# Run tests
npm test

# Build for production
npm run build
🔍 Search Examples
Example Queries
Science Content: "mysteries of quantum physics"

Educational: "how to learn programming"

Entertainment: "funny animal videos"

News: "latest technology updates 2024"

Tutorials: "Python programming tutorials"

Expected Results Format
json
{
  "query": "your search query",
  "results_count": 10,
  "results": [
    {
      "rank": 1,
      "video_id": "abc123",
      "title": "Video Title",
      "channel": "Channel Name",
      "similarity_score": 0.9567,
      "views": 15000,
      "summary": "AI-generated summary...",
      "duration": "15:30"
    }
  ]
}
🚀 Deployment Guide
Local Development
bash
# Backend
python main.py

# Frontend
npm start

# Access at:
# UI: http://localhost:3000
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
Production Considerations
Environment Variables: Configure API keys and paths

CORS Settings: Update allowed origins for production domain

Database Paths: Use absolute paths for persistence

Error Logging: Implement proper logging for production

Security: Add authentication for protected endpoints

📱 Features Roadmap
Planned Enhancements
Advanced Filters

Duration range filtering

Date published filtering

View count thresholds

Category/tag filtering

Enhanced UI

Dark/light theme toggle

Responsive design improvements

Video preview thumbnails

Advanced sorting options

Additional Features

User accounts and favorites

Search history

Export search results

Video recommendation engine

🆘 Troubleshooting
Common Issues
Ollama Not Found

bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull the model
ollama pull llama3.2
ChromaDB Connection Issues

bash
# Check database path
python -c "import chromadb; client = chromadb.PersistentClient(path='./chroma_db')"

# Rebuild database if needed
python setup_chromadb.py
CORS Errors

Ensure backend CORS settings include frontend origin

Check browser console for specific error messages

Verify both servers are running

Monitoring
bash
# Check backend status
curl http://localhost:8000/health

# Check summarizer status
curl http://localhost:8000/summarizer/status

# Test database connection
curl http://localhost:8000/debug/db
📚 Additional Resources
Documentation
FastAPI Docs

ChromaDB Docs

Ollama Docs

React Docs

Models Used
Embedding Model: all-MiniLM-L6-v2 (384 dimensions)

Summarization Model: llama3.2 via Ollama

Vector Database: ChromaDB (persistent storage)

Dataset Information
Total Videos: 615

Source: YouTube API + custom collection

Fields: Title, transcript, channel, views, duration, tags

Embeddings: Pre-computed using sentence-transformers

🤝 Contributing
We welcome contributions! Please follow these steps:

Fork the repository

Create a feature branch (git checkout -b feature/AmazingFeature)

Commit your changes (git commit -m 'Add some AmazingFeature')

Push to the branch (git push origin feature/AmazingFeature)

Open a Pull Request

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

🎯 Quick Links
Live Demo: http://localhost:3000

API Docs: http://localhost:8000/docs

Health Check: http://localhost:8000/health

Source Code: GitHub Repository

Issue Tracker: GitHub Issues

Start exploring 615+ YouTube videos with semantic intelligence! 🚀

Search, discover, and summarize content like never before with our AI-powered YouTube search engine.


