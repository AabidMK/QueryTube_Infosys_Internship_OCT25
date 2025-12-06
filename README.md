QueryTube: YouTube Video Semantic Search & Summarization System
📌 Overview
QueryTube is an advanced semantic search and summarization system for YouTube videos that enables intelligent content discovery through vector embeddings and AI-powered analysis.

🎯 Features
🔍 Semantic Video Search: Find relevant videos using natural language queries

🧠 AI-Powered Summarization: Generate concise summaries of video content

📊 Vector Database Integration: Store and query video embeddings using ChromaDB

🎬 Metadata Analysis: Extract and analyze video information (title, channel, views, duration)

📝 Transcript Processing: Process and utilize video transcripts for better search results

🏗️ Project Structure
Core Modules:
text
QueryTube/
│
├── 📁 chroma_db/                 # ChromaDB vector database storage
├── 📁 data/                      # Dataset and embeddings
├── 📁 scripts/                   # Main system scripts
│   ├── 🔧 setup_chromadb.py      # Database initialization and setup
│   ├── 🔍 query_system.py        # Main semantic search system
│   ├── 🎯 query_chromadb.py      # Advanced vector search interface
│   ├── 🤖 video_summarizer.py    # AI-powered video summarization
│   ├── 🐛 debug.py               # Debugging and testing utilities
│   └── 📊 dataset_with_embeddings.csv  # Pre-computed video embeddings
│
├── 📁 examples/                  # Sample outputs and results
│   ├── 📄 summary_t8txtQkhMcY_20251203_152445.json
│   └── 📄 search_results.json
│
└── 📖 README.md                  # This documentation file
🚀 Quick Start
Prerequisites
bash
pip install chromadb sentence-transformers pandas numpy ollama
Setup Database
bash
# 1. Prepare the vector database
python setup_chromadb.py

# Expected output:
# ✅ Database setup complete with X videos
Run Semantic Search
bash
# Interactive search interface
python query_system.py

# Command-line search
python query_chromadb.py
Generate Video Summaries
bash
# Interactive mode
python video_summarizer.py

# Summarize specific video
python video_summarizer.py <video_id>
📋 Core Components
1. Database Setup (setup_chromadb.py)
Parses video dataset with pre-computed embeddings

Initializes ChromaDB vector database

Stores video metadata, transcripts, and embeddings

Key features: Batch processing, error handling, data validation

2. Semantic Search System (query_system.py)
python
from query_system import VideoSearchSystem

# Initialize system
search_system = VideoSearchSystem()

# Search for videos
results = search_system.search_videos_by_query(
    "machine learning tutorials", 
    n_results=5
)

# Interactive search
search_system.interactive_search()
3. Advanced Vector Search (query_chromadb.py)
Multi-modal search capabilities

Similarity-based video recommendations

Metadata filtering and ranking

Support for text-based and embedding-based queries

4. AI Video Summarizer (video_summarizer.py)
python
from video_summarizer import WorkingVideoSummarizer

# Initialize summarizer
summarizer = WorkingVideoSummarizer()

# Generate summary
summary = summarizer.create_summary("t8txtQkhMcY")

# Display and save
summarizer.show_summary(summary)
summarizer.save_summary(summary)
5. Debugging Tools (debug.py)
Database integrity checks

ID validation and verification

Embedding quality assessment

Error diagnosis and troubleshooting

📊 Data Schema
Video Metadata Structure:
json
{
  "id": "video_id",
  "title": "Video Title",
  "channel_title": "Channel Name",
  "view_count": 12345,
  "duration": "PT1H23M45S",
  "transcript": "Full transcript text...",
  "published_at": "2024-01-01T00:00:00Z",
  "tags": "tag1, tag2, tag3",
  "category_id": 27,
  "embedding": [0.1, 0.2, ..., 0.384]
}
Search Result Format:
json
{
  "query": "search query",
  "timestamp": "2025-12-03T11:12:23.895910",
  "results": [
    {
      "video_id": "abc123",
      "title": "Video Title",
      "channel_name": "Channel Name",
      "similarity_score": 0.85
    }
  ]
}
🔧 Configuration
Embedding Model
Model: all-MiniLM-L6-v2

Dimensions: 384

Usage: Video and query encoding

Vector Database
Database: ChromaDB (Persistent)

Collection: youtube_videos

Path: ./chroma_db

AI Summarization
Model: llama3.2 (via Ollama)

Fallback: Basic extractive summarization

Output: 2-3 sentence summaries

📈 Performance Metrics
Search Accuracy
Semantic similarity matching

Relevance ranking based on cosine similarity

Multi-factor scoring (metadata + embeddings)

Summarization Quality
AI-generated summaries using LLMs

Basic extractive fallback when AI unavailable

Cleaned and processed transcript inputs

🎮 Usage Examples
Example 1: Find Similar Videos
python
# Find videos similar to a known video
db = VideoVectorDB()
similar_videos = db.search_similar_to_video(
    "t8txtQkhMcY",  # Tibet mountain mystery
    n_results=5
)
Example 2: Interactive Search
bash
# Run interactive interface
python query_system.py

# Enter queries like:
# "ancient mysteries"
# "science documentaries"
# "coding tutorials"
Example 3: Batch Processing
python
# Summarize multiple videos
videos_to_summarize = ["id1", "id2", "id3"]
for video_id in videos_to_summarize:
    summary = summarizer.create_summary(video_id)
    print(f"Summary for {video_id}: {summary['summary'][:100]}...")
🛠️ Troubleshooting
Common Issues & Solutions:
Database Connection Failed

bash
# Reinitialize database
rm -rf chroma_db/
python setup_chromadb.py
Missing Embeddings

bash
# Check dataset file
python debug.py
Ollama Not Available

Install Ollama: curl -fsSL https://ollama.ai/install.sh | sh

Pull model: ollama pull llama3.2

Or use basic summarization mode

Video Not Found

bash
# Check video ID in database
python debug.py
📚 Dataset Information
Source:
YouTube videos with complete metadata

Pre-computed sentence embeddings

Cleaned and processed transcripts

Columns in dataset_with_embeddings.csv:
id: YouTube video ID

title: Video title

channel_title: Channel name

viewCount: View count

duration: Video duration

transcript: Full transcript text

publishedAt: Upload date

tags: Video tags

categoryId: YouTube category

embeddings: Pre-computed 384-dim embeddings

🔮 Future Enhancements
Planned Features:
Real-time YouTube API integration

Multi-language support

User preference learning

Advanced filtering options

Web interface with Streamlit/FastAPI

Collaborative filtering

Trend analysis

Cross-modal search (audio + video)

Performance Improvements:
Parallel processing for batch operations

Caching for frequent queries

Optimized embedding storage

GPU acceleration support

🤝 Contributing
Setup Development Environment:
bash
# Clone repository
git clone https://github.com/AabidMK/QueryTube_Infosys_Internship_OCT25.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
Contribution Guidelines:
Fork the repository

Create a feature branch

Add tests for new functionality

Ensure code follows PEP8 style

Submit pull request with detailed description

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.



🙏 Acknowledgments
ChromaDB team for vector database solution

SentenceTransformers for embedding models

Ollama for local LLM access

YouTube Data API for video metadata

🚨 Important Notes
Before Running:
Ensure you have sufficient disk space for database (500MB+)

Internet connection required for AI summarization

Python 3.8+ required

At least 4GB RAM recommended

Quick Test:
bash
# Test the entire system
python -c "import sys; sys.path.insert(0, '.'); from query_system import VideoSearchSystem; s = VideoSearchSystem(); print('✅ System ready!' if s.is_ready() else '❌ System error')"
✨ Ready to explore YouTube videos intelligently? Start with python query_system.py!