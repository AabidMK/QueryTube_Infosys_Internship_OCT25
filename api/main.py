from fastapi import FastAPI, HTTPException, UploadFile, File, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import io
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
import os
import numpy as np
import json
import traceback
import pickle
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import google.generativeai as genai
from dotenv import load_dotenv  # Add this import

# Load environment variables from .env file
load_dotenv()

# Create router with API prefix
api_router = APIRouter(prefix="/api")

app = FastAPI(
    title="Semantic Video Search API",
    description="API for semantic search and analysis of video content using AI embeddings",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class SearchQuery(BaseModel):
    query: str
    top_k: int = 5

class SearchResult(BaseModel):
    id: str
    title: str
    channel: str
    views: Any
    duration: str
    similarity_score: float
    keyword_in_title: bool
    keyword_in_transcript: bool
    relevance: str
    preview: str
    metadata: Dict[str, Any]

class SearchResponse(BaseModel):
    results: List[SearchResult]
    query: str
    total_results: int
    average_similarity: float
    max_similarity: float
    search_type: str

class IngestionResponse(BaseModel):
    id: str
    status: str
    message: str
    timestamp: str
    ingested_count: int
    error_count: int
    total_chunks: int

# Configuration
class Config:
    def __init__(self):
        # File path configuration - faiss_videos_db folder outside current folder
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.faiss_db_path = os.path.join(self.base_dir, "vectors", "faiss_videos_db")
        
        # File paths
        self.index_file = os.path.join(self.faiss_db_path, "faiss.index")
        self.metadata_file = os.path.join(self.faiss_db_path, "metadata.pkl")
        
        self.gemini_model = None
        self._setup_gemini()

        # Create directories if they don't exist
        os.makedirs(self.faiss_db_path, exist_ok=True)
        
        print(f"🔧 Configuration loaded:")
        print(f"   - Base directory: {self.base_dir}")
        print(f"   - FAISS DB path: {self.faiss_db_path}")

    def _setup_gemini(self):
        """Setup Gemini API for summary generation"""
        try:
            # Load API key from environment
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                print("❌ GEMINI_API_KEY environment variable not set")
                return
            
            genai.configure(api_key=api_key)
            self.gemini_model = genai.GenerativeModel('gemini-flash-latest')
            print("✅ Gemini Flash model configured successfully")
        except Exception as e:
            print(f"❌ Error setting up Gemini: {e}")

# FAISS Vector Database with Semantic Search
class FAISSVectorDB:
    def __init__(self):
        print("🚀 Initializing FAISS VectorDB with Semantic Search...")
        self.config = Config()
        self.embedding_model = None
        self.index = None
        self.metadata = []
        self.documents = []
        
        self._load_embedding_model()
        self._load_faiss_index()
        print("✅ FAISS VectorDB initialized successfully!")
    
    def _load_embedding_model(self):
        """Load SentenceTransformer model for semantic search"""
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            print("✅ Loaded SentenceTransformer model for semantic search")
        except Exception as e:
            print(f"❌ Failed to load embedding model: {e}")
            self.embedding_model = None
    
    def _load_faiss_index(self):
        """Load FAISS index and metadata"""
        try:
            if os.path.exists(self.config.index_file) and os.path.exists(self.config.metadata_file):
                import faiss
                self.index = faiss.read_index(self.config.index_file)
                with open(self.config.metadata_file, 'rb') as f:
                    data = pickle.load(f)
                    self.metadata = data.get('metadata', [])
                    self.documents = data.get('documents', [])
                print(f"✅ Loaded FAISS index with {len(self.metadata)} videos")
            else:
                print("❌ FAISS database not found. Please run vector.py first.")
                # Initialize empty data structures
                self.metadata = []
                self.documents = []
        except Exception as e:
            print(f"❌ Error loading FAISS index: {e}")
            # Initialize empty data structures even if loading fails
            self.metadata = []
            self.documents = []
    
    def semantic_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Perform semantic search using SentenceTransformer and cosine similarity"""
        if self.embedding_model is None:
            raise HTTPException(status_code=500, detail="Search engine not properly initialized")
        
        if not self.documents:
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])
            
            results = []
            
            for i, (doc, metadata) in enumerate(zip(self.documents, self.metadata)):
                # Generate document embedding
                doc_embedding = self.embedding_model.encode([doc])
                
                # Calculate cosine similarity
                similarity = cosine_similarity(query_embedding, doc_embedding)[0][0]
                
                # Check for keyword matches
                title = metadata.get('title', '').lower()
                transcript_lower = doc.lower()
                query_lower = query.lower()
                
                keyword_in_title = query_lower in title
                keyword_in_transcript = query_lower in transcript_lower
                
                # Determine relevance level
                similarity_score = float(similarity)
                if similarity_score >= 0.8:
                    relevance = "Highly Relevant"
                elif similarity_score >= 0.6:
                    relevance = "Very Relevant"
                elif similarity_score >= 0.4:
                    relevance = "Moderately Relevant"
                elif similarity_score >= 0.2:
                    relevance = "Somewhat Relevant"
                else:
                    relevance = "Low Relevance"
                
                # Create preview snippet
                preview = doc[:200] + "..." if len(doc) > 200 else doc
                
                results.append({
                    'id': metadata.get('original_id', f"video_{i}"),
                    'title': metadata.get('title', 'Unknown Title'),
                    'channel': metadata.get('channel_title', 'Unknown Channel'),
                    'views': metadata.get('view_count', 'N/A'),
                    'duration': metadata.get('duration', 'N/A'),
                    'similarity_score': similarity_score,
                    'keyword_in_title': keyword_in_title,
                    'keyword_in_transcript': keyword_in_transcript,
                    'relevance': relevance,
                    'preview': preview,
                    'metadata': metadata
                })
            
            # Sort by similarity score (highest first)
            results.sort(key=lambda x: x['similarity_score'], reverse=True)
            return results[:top_k]
            
        except Exception as e:
            print(f"❌ Semantic search error: {e}")
            raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
    
    def add_documents(self, documents: List[str], metadatas: List[Dict[str, Any]]):
        """Add documents to the in-memory database (for demo purposes)"""
        self.documents.extend(documents)
        self.metadata.extend(metadatas)
        print(f"✅ Added {len(documents)} documents to in-memory database")
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get database information"""
        total_videos = len(self.metadata)
        
        return {
            "total_videos": total_videos,
            "database_path": self.config.faiss_db_path,
            "search_engine": "SentenceTransformer + Cosine Similarity",
            "status": "ready" if self.embedding_model else "error"
        }
    
    def get_document_by_id(self, doc_id):
        """Get document by ID"""
        for i, metadata in enumerate(self.metadata):
            if metadata.get('original_id') == doc_id:
                return {
                    'id': doc_id,
                    'document': self.documents[i],
                    'metadata': metadata
                }
        return None
    
    def get_video_statistics(self, doc_id):
        """Get basic statistics for a video"""
        video_data = self.get_document_by_id(doc_id)
        if not video_data:
            return None
        
        transcript = video_data['document']
        metadata = video_data['metadata']
        
        stats = {
            'id': doc_id,
            'title': metadata.get('title', 'N/A'),
            'channel': metadata.get('channel_title', 'N/A'),
            'views': metadata.get('view_count', 'N/A'),
            'duration': metadata.get('duration', 'N/A'),
            'transcript_length': len(transcript),
            'word_count': len(transcript.split()),
            'sentence_count': len([s for s in transcript.split('.') if s.strip()]),
            'avg_word_length': sum(len(word) for word in transcript.split()) / len(transcript.split()) if transcript.split() else 0
        }
        
        return stats

# Add Pydantic model for summary response
class VideoSummaryResponse(BaseModel):
    id: str
    title: str
    channel: str
    views: Any
    duration: str
    summary: str
    statistics: Dict[str, Any]
    generated_at: str

# Add helper function to generate summary
def generate_video_summary(model, video_data):
    """Generate summary using Gemini Flash model"""
    try:
        prompt = f"""
        Please analyze this video data and provide a comprehensive summary in the following format:
        
        **Video Summary**
        
        **Title:** [Video Title]
        **Channel:** [Channel Name]
        **Views:** [View Count]
        
        **Key Insights:**
        - Provide 3 key insights about the video content
        - Focus on main topics discussed
        - Highlight interesting patterns or themes
        
        **Content Analysis:**
        - Summarize the main content in 2-3 paragraphs
        - Identify the primary purpose of the video
        - Note any unique or standout elements
        
        
        Video Data:
        Title: {video_data['metadata'].get('title', 'N/A')}
        Channel: {video_data['metadata'].get('channel_title', 'N/A')}
        Views: {video_data['metadata'].get('view_count', 'N/A')}
        Duration: {video_data['metadata'].get('duration', 'N/A')}
        
        Transcript:
        {video_data['document'][:4000]}  # Limit transcript length for API
        
        Please provide a well-structured, insightful summary that captures the essence of this video.
        """
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"❌ Error generating summary: {e}"

# Initialize the database
vector_db = FAISSVectorDB()

# API endpoints
@api_router.get("/")
async def api_root():
    return {
        "message": "Semantic Video Search API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "health": "GET /api/health",
            "search": "POST /api/search",
            "ingest": "POST /api/ingest",
            "summary": "GET /api/summary/{video_id}"
        },
        "search_engine": "Semantic Search with SentenceTransformer"
    }

@api_router.get("/health")
async def health_check():
    info = vector_db.get_database_info()
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "total_videos": info.get("total_videos", 0),
        "search_engine_ready": info.get("status") == "ready",
        "api_version": "1.0.0"
    }

@api_router.post("/search", response_model=SearchResponse)
async def search_videos(search_query: SearchQuery):
    """Search videos using semantic search"""
    try:
        print(f"🔍 Semantic search request: '{search_query.query}'")
        
        results = vector_db.semantic_search(
            query=search_query.query,
            top_k=search_query.top_k
        )
        
        if not results:
            return SearchResponse(
                results=[],
                query=search_query.query,
                total_results=0,
                average_similarity=0.0,
                max_similarity=0.0,
                search_type="semantic"
            )
        
        # Calculate statistics
        similarities = [r['similarity_score'] for r in results]
        avg_similarity = sum(similarities) / len(similarities)
        max_similarity = max(similarities)
        
        return SearchResponse(
            results=results,
            query=search_query.query,
            total_results=len(results),
            average_similarity=round(avg_similarity, 4),
            max_similarity=round(max_similarity, 4),
            search_type="semantic"
        )
        
    except Exception as e:
        print(f"❌ Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/ingest", response_model=IngestionResponse)
async def ingest_document(file: UploadFile = File(...)):
    """
    Ingest documents from a CSV file
    CSV must have columns: id, title, channel_title, view_count, duration, transcript
    """
    try:
        print(f"🔍 DEBUG: Starting ingest endpoint")
        print(f"📥 Received file: {file.filename}")
        print(f"📥 Content type: {file.content_type}")
        
        # Validate file type
        if not file.filename.lower().endswith('.csv'):
            print("❌ File is not CSV")
            raise HTTPException(status_code=400, detail="File must be a CSV")
        
        # Read file
        contents = await file.read()
        print(f"📥 File size: {len(contents)} bytes")
        
        if len(contents) == 0:
            print("❌ File is empty")
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Parse CSV
        try:
            df = pd.read_csv(io.BytesIO(contents))
            print(f"✅ CSV read successfully. Shape: {df.shape}")
            print(f"✅ Columns: {df.columns.tolist()}")
        except Exception as e:
            print(f"❌ CSV reading failed: {str(e)}")
            print(f"❌ Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=400, detail=f"Invalid CSV format: {str(e)}")
        
        # Check required columns
        required_columns = ['transcript']  # Only transcript is strictly required
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"❌ Missing required columns: {missing_columns}")
            raise HTTPException(status_code=400, detail=f"Missing required columns: {missing_columns}")
        
        # Optional columns with defaults
        text_column = 'transcript'
        id_column = 'id' if 'id' in df.columns else None
        title_column = 'title' if 'title' in df.columns else 'title_cleaned' if 'title_cleaned' in df.columns else None
        channel_column = 'channel_title' if 'channel_title' in df.columns else 'channel' if 'channel' in df.columns else None
        views_column = 'view_count' if 'view_count' in df.columns else 'views' if 'views' in df.columns else None
        duration_column = 'duration' if 'duration' in df.columns else 'duration_seconds' if 'duration_seconds' in df.columns else None
        
        print(f"✅ Using columns:")
        print(f"   - Text: {text_column}")
        print(f"   - ID: {id_column}")
        print(f"   - Title: {title_column}")
        print(f"   - Channel: {channel_column}")
        print(f"   - Views: {views_column}")
        print(f"   - Duration: {duration_column}")
        
        ingested_count = 0
        error_count = 0
        documents = []
        metadatas = []
        
        # Process each row
        for index, row in df.iterrows():
            try:
                text = str(row[text_column]).strip()
                if not text or text.lower() == 'nan' or text.lower() == 'none':
                    print(f"⚠️ Row {index}: Empty text, skipping")
                    error_count += 1
                    continue
                
                # Extract metadata
                metadata = {}
                if id_column and pd.notna(row.get(id_column)):
                    metadata['original_id'] = str(row[id_column])
                else:
                    metadata['original_id'] = f"doc_{index}_{uuid.uuid4().hex[:8]}"
                    
                if title_column and pd.notna(row.get(title_column)):
                    metadata['title'] = str(row[title_column])
                else:
                    metadata['title'] = f"Document {index}"
                    
                if channel_column and pd.notna(row.get(channel_column)):
                    metadata['channel_title'] = str(row[channel_column])
                else:
                    metadata['channel_title'] = "Unknown Channel"
                    
                if views_column and pd.notna(row.get(views_column)):
                    metadata['view_count'] = int(row[views_column]) if str(row[views_column]).replace('.','').isdigit() else str(row[views_column])
                else:
                    metadata['view_count'] = "N/A"
                    
                if duration_column and pd.notna(row.get(duration_column)):
                    metadata['duration'] = str(row[duration_column])
                else:
                    metadata['duration'] = "N/A"
                
                print(f"📝 Processing row {index} ({len(text)} chars): {text[:100]}...")
                
                # Add to documents and metadata
                documents.append(text)
                metadatas.append(metadata)
                ingested_count += 1
                
                if ingested_count % 100 == 0:
                    print(f"✅ Processed {ingested_count} rows...")
                
            except Exception as e:
                error_msg = f"Row {index}: {str(e)}"
                print(f"❌ {error_msg}")
                error_count += 1
        
        # Add documents to vector database
        if documents:
            vector_db.add_documents(documents, metadatas)
        
        print(f"✅ Ingestion complete: {ingested_count} documents, {error_count} errors")
        
        return IngestionResponse(
            id=str(uuid.uuid4()),
            status="success",
            message=f"CSV processed successfully. {ingested_count} documents added to vector database.",
            timestamp=datetime.now().isoformat(),
            ingested_count=ingested_count,
            error_count=error_count,
            total_chunks=ingested_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Endpoint error: {str(e)}")
        print(f"❌ Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Add the summary endpoint
@api_router.get("/summary/{video_id}", response_model=VideoSummaryResponse)
async def get_video_summary(video_id: str):
    """Get AI-generated summary for a specific video"""
    try:
        print(f"📝 Generating summary for video: {video_id}")
        
        # Get video data from vector database
        video_data = vector_db.get_document_by_id(video_id)
        if not video_data:
            raise HTTPException(status_code=404, detail=f"Video with ID '{video_id}' not found")
        
        # Get video statistics
        statistics = vector_db.get_video_statistics(video_id)
        if not statistics:
            raise HTTPException(status_code=404, detail=f"Could not retrieve statistics for video '{video_id}'")
        
        # Generate AI summary if Gemini is available
        summary = "Summary generation not available - Gemini API not configured"
        if vector_db.config.gemini_model:
            try:
                summary = generate_video_summary(vector_db.config.gemini_model, video_data)
            except Exception as e:
                summary = f"❌ Error generating AI summary: {str(e)}"
        else:
            summary = "Gemini API not configured - cannot generate AI summary"
        
        return VideoSummaryResponse(
            id=video_id,
            title=statistics['title'],
            channel=statistics['channel'],
            views=statistics['views'],
            duration=statistics['duration'],
            summary=summary,
            statistics=statistics,
            generated_at=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Summary generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")

# Include the router with /api prefix
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Semantic Video Search API Server...")
    print("📚 API Endpoints (all under /api):")
    print("   GET  /api/          - API information")
    print("   GET  /api/health    - Health check")
    print("   POST /api/search    - Semantic search")
    print("   POST /api/ingest    - Upload CSV file")
    print("   GET  /api/summary/{video_id} - Get AI-generated video summary")
    print("\n🔧 Configuration:")
    print(f"   - Database path: {vector_db.config.faiss_db_path}")
    print(f"   - Search engine: SentenceTransformer + Cosine Similarity")
    print(f"   - Embedding model: all-MiniLM-L6-v2")
    print(f"   - Gemini model: {'Configured' if vector_db.config.gemini_model else 'Not Configured'}")
    print(f"\n🔗 API Base URL: http://localhost:8000/api")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)