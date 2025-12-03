# 1) Video Data Extraction
## Overview
A Python script to fetch complete video data from YouTube channels using the YouTube Data API v3.

🚀 Features
- Extracts detailed video information (titles, descriptions, statistics)
- Fetches channel metadata 
- Ensures only complete data (no missing critical fields)
- Exports to CSV format with proper encoding
  

📋 Prerequisites
Python 3.x
YouTube Data API v3 key

Install dependencies:

``` bash
pip install google-api-python-client pandas python-dotenv
``` 
### Get API Key:

- Go to Google Cloud Console
- Enable YouTube Data API v3
- Create API credentials

### Configure Environment:
- Create a .env file in the same directory
- YOUTUBE_API_KEY=your_api_key_here
- Open the script and update the channel ID:
- CHANNEL_ID = "UCsT0YIqwnpJCM-mx7-gSA4Q"  # TEDx Talks (default)
- CHANNEL_ID = "YOUR_CHANNEL_ID_HERE"    # Your channel

Run the script:
``` bash
python yt_data.py
```
📊 Output
The script creates Tedx_talks_data.csv containing:

#### Video Data:
Title, Description, Duration
View count, Like count, Comment count
Published date, Tags, Thumbnail URLs
Privacy status
#### Channel Data:
Channel title, description
Subscriber count, video count
Country

# 2) Extract YouTube Transcript 
A Python script that extracts and cleans English transcripts from YouTube videos using the Supadata API. The tool processes multiple videos, filters for English content, removes audio tags, and saves transcripts in a structured CSV format.

🚀 Features
- Multi-video processing - Handles batches of 50+ video IDs
- English language filtering - Extracts only English transcript content
-  Automatic cleaning - Removes [Music], [Applause], and other audio tags
-  Error handling - Robust error handling for missing transcripts
-  CSV export - Saves transcripts with metadata (word count, status)

📋 Prerequisites
Python 3.x or higher
Supadata API key (from Supadata)
#### Required Python packages:
supadata
python-dotenv

🔧 Installation & Setup
1. Install Dependencies
```bash
pip install supadata python-dotenv
```
2. Get Supadata API Key
- Sign up at Supadata
- Generate your API key from the dashboard
- Copy your API key

3. Configure Environment
- Create a .env file in your project directory
- SUPADATA_API_KEY=your_supadata_api_key_here


#### ⚡ Quick Start
1. Prepare Video IDs
Edit the video_ids list in the script:
python
video_ids = ['video_id_1', 'video_id_2', 'video_id_3']  # Your YouTube video IDs

3. Run the Script
bash
python extract_transcripts.py
📊 Output
The script creates english_video_transcripts.csv containing:

### Column	Description
video_id	YouTube video ID
raw_transcript	Original extracted transcript
cleaned_transcript	Cleaned English text
status	success/failed
word_count	Number of words in cleaned transcript
language_notes	Language detection notes


### ⚙️ Configuration Options
- Setting	Description	Default
- Delay between API requests (seconds)	0.5
- sample_size	Number of videos for preview	3
#### 📁 Functions Overview
Main Functions:
- extract_text_from_transcript_data() - Extracts English text from structured data
- clean_transcript() - Removes audio tags and cleans text
- extract_transcripts_to_csv() - Main extraction and export function
- preview_transcript_structure() - Preview language distribution


# 3) Dataset Preprocessing & Embedding 
A comprehensive data preprocessing pipeline that cleans, processes, and generates embeddings for YouTube video data using sentence transformers.

🚀 Features
- Text Cleaning - Lowercasing, punctuation removal, whitespace normalization

- Duration Conversion - Converts ISO 8601 duration to seconds

- Embedding Generation - Creates semantic embeddings using all-MiniLM-L6-v2

- Chunk Processing - Handles long transcripts with overlapping chunks

- PyTorch Integration - Pure PyTorch tensor operations to avoid NumPy issues

- Multi-column Processing - Processes titles, descriptions, and transcripts

📋 Dependencies
``` bash
pip install pandas numpy torch sentence-transformers
```
🔧 Processing Pipeline
#### 1. Data Loading
df = pd.read_csv('master_dataset_updated.csv')
#### Input Columns:
id, title, description, transcript
duration, viewCount, likeCount, etc.
Channel metadata and statistics

#### 2. Text Cleaning Function
``` bash
def clean_text(text):
    # Converts to lowercase
    # Removes punctuation and special characters
    # Normalizes whitespace
    # Handles NaN and non-string values
```
#### 3. Duration Processing
``` bash
df['duration_seconds'] = pd.to_timedelta(df['duration'], errors='coerce').dt.total_seconds()
Converts ISO 8601 format (e.g., PT3H59M26S) to seconds
```
Handles conversion errors gracefully

#### 4. Embedding Generation
Model: sentence-transformers/all-MiniLM-L6-v2 (384 dimensions)
Title + Transcript Combined - Semantic representation of video content


#### 5. Chunk Processing for Long Texts
```bash
def chunk_text(text, max_tokens=500, overlap=50):
    # Splits long texts into manageable chunks
    # Maintains context with overlapping chunks
    # Returns list of text chunks
```

- max_tokens:	Maximum tokens per chunk	500
- overlap:	Overlapping tokens between chunks	50
- model_name:	Sentence transformer model	all-MiniLM-L6-v2

# 4) FAISS Vector Database Storage
Python script to store video embeddings in a FAISS vector database with metadata management.

####  Setup
``` bash
pip install faiss-cpu pandas numpy
```
#### Required Input File
final_embeddings.csv in current directory

#####  Usage
```bash
python vector.py
```
##  What It Does
#### 1. Loads Data
- Reads final_embeddings.csv
- Extracts video embeddings from e_title_trans_tensor column

#### 2. Processes Embeddings
- Converts tensor strings to numeric arrays
- Validates embedding dimensions and quality
- Handles missing/invalid embeddings

#### 3. Creates FAISS Database
- Stores embeddings in ./faiss_videos_db/
- Creates faiss.index and metadata.pkl
- Saves comprehensive metadata to metadata_mapping.pkl

#### 4. Output Files
```text
faiss_videos_db/
├── faiss.index
└── metadata.pkl
metadata_mapping.pkl
```
## Statistics Tracked
- Successful/failed embedding conversions
- Embedding dimensions (typically 384)
- Video metadata preservation
- Ingestion timestamp

## Core Functions
- convert_tensor_string() - Parse embedding strings
- validate_embedding() - Check embedding validity
- FAISSVectorDB class - Manage vector database
- create_and_save_metadata_mapping() - Backup metadata

# 5) Semantic Video Search Engine 🔍
A semantic search system that finds relevant YouTube videos using AI embeddings and FAISS vector database.

### Setup

```bash
pip install faiss-cpu sentence-transformers scikit-learn pandas numpy
```
Required Files
- FAISS database created by previous script (./faiss_videos_db/)
- Must have run vector_db.py first

## Usage
```bash
python semantic_search.py
```
## What It Does
#### 1. Initialization
- Loads FAISS index and metadata

- Loads all-MiniLM-L6-v2 sentence transformer model

- Prepares for semantic search

#### 2. Semantic Search Process
- Encodes user query into embedding vector

- Calculates cosine similarity between query and all video transcripts

- Ranks videos by semantic similarity

- Returns top N most relevant results

#### 3. Features
- Semantic similarity scoring

- Keyword match highlighting (title/transcript)

- Relevance interpretation (High/Very/Moderate/Somewhat/Low)

- Key insight extraction from transcripts

#### 4. Interactive Interface
```text
🔍 Enter your search query: machine learning tutorial
📊 Number of results to show (default 5): 10
```
##  Output Format
For each result:

```text
1. 📹 VIDEO RESULT
   🆔 ID: [video_id]
   📺 Title: [video_title]
   🏢 Channel: [channel_name]
   👀 Views: [view_count]
   ⏱️ Duration: [duration]
   🧠 Semantic Similarity: 0.8563
   🔍 ✅ Keyword in Title
   📊 Relevance: 🎯 Highly Relevant
   💡 Key Insight: [most relevant sentence]
```
# 6) AI Video Summary Generator 🤖

Interactive tool that uses Google's Gemini Flash AI to generate comprehensive summaries of YouTube videos.
## Setup

```bash
pip install google-generativeai faiss-cpu
```
Required Files
-.env file with your Gemini API key:

```text
GEMINI_API_KEY=your_gemini_api_key_here
FAISS database
metadata_mapping.pkl file
```

## Usage
```bash
python video_summary.py
```
## What It Does
#### 1. Initialization
- Loads environment variables from .env file

- Configures Gemini Flash model (gemini-flash-latest)

- Loads FAISS database with video metadata and transcripts

#### 2. Interactive Menu
``` text
📊 FAISS VIDEO DATABASE - AI SUMMARY GENERATOR
==================================================
🎬 VIDEO SUMMARY GENERATOR
==================================================
1. 📝 Generate AI Summary for Video
2. 📊 Show Video Statistics
3. 🔍 Find Video ID (List some videos)
4. 🚪 Exit
3. Option 1: Generate AI Summary
Enter video ID

System retrieves video metadata and transcript

Uses Gemini Flash to generate comprehensive summary:

Key insights (3-5 points)

Content analysis (2-3 paragraphs)

Transcript highlights (notable quotes)

Option to save summary to text file

4. Option 2: Show Video Statistics
Basic video analytics:

Transcript length (characters)

Word count

Sentence count

Average word length

Estimated reading time

5. Option 3: Find Video ID
Lists sample videos from database

Shows ID, title, channel, views, and transcript preview

Helps users discover available videos
```
### AI Summary Features
- Structured Format: Clear sections with bullet points

- Content Analysis: Identifies main topics and purpose

- Highlight Extraction: Pulls notable quotes from transcript

- Insight Generation: Provides 3-5 key takeaways

### Configuration
- Uses gemini-flash-latest model (fast and cost-effective)

- Transcripts truncated to 4000 characters for API limits

- Automatic .env file loading for API key security

## Requirements
- Valid Gemini API key in .env file

- Completed FAISS database from previous steps

- Python packages: google-generativeai, faiss-cpu

# 7) FastAPI Semantic Video Search API 🚀
FastAPI backend for semantic video search, ingestion, and AI summarization.

## Setup
```bash
pip install fastapi uvicorn sentence-transformers google-generativeai faiss-cpu pandas python-dotenv scikit-learn
```
 Run Server
```bash
uvicorn main:app --relad
```
📡 API Endpoints
- Base URL: http://localhost:8000/api
- GET /api/ - API information
- GET /api/health - Health check
- POST /api/search - Semantic search
- POST /api/ingest - Upload CSV with videos
- GET /api/summary/{video_id} - AI-generated video summary
#### 📊 Features
- Semantic search using SentenceTransformer embeddings

- Cosine similarity ranking

- CSV file ingestion (requires transcript column)

- AI summaries using Gemini Flash

- Health monitoring

### Input Requirements
- .env file with GEMINI_API_KEY
- FAISS database in vectors/faiss_videos_db/
- CSV files for ingestion must have transcript column


