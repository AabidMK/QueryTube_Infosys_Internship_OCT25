import faiss
from pathlib import Path
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

app = FastAPI(
    title="Semantic Video Search API",
    description="API for semantic search and analysis of video content using AI embeddings",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://querytube-ai.vercel.app",  # Your Vercel frontend
        "http://localhost:3000",
        "http://127.0.0.1:3000"  # Local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Create router with API prefix
api_router = APIRouter(prefix="/api")

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
# Configuration
class Config:
    def __init__(self):
        # Check if running on Render
        self.is_render = os.environ.get('RENDER') is not None
        
        # Hugging Face Repository Info
        self.hf_repo_id = "karunya-3/faiss-video-db"  # Your repository
        self.hf_files = {
            "index": "faiss.index",
            "metadata": "metadata.pkl"
        }
        
        # Set paths based on environment
        if self.is_render:
            # Render production paths - use a persistent directory
            self.base_dir = Path("/opt/render")
            self.faiss_cache_dir = self.base_dir / "faiss_cache"
            print("🚀 Running in RENDER environment")
            print(f"📂 Cache directory: {self.faiss_cache_dir}")
        else:
            # Local development paths
            self.base_dir = Path(__file__).parent.parent
            self.faiss_cache_dir = self.base_dir / "faiss_cache"
        
        # Create cache directory if it doesn't exist
        os.makedirs(self.faiss_cache_dir, exist_ok=True)
        
        # File paths (will be set after download)
        self.index_file = None
        self.metadata_file = None
        
        self.gemini_model = None
        self._setup_gemini()

    def _setup_gemini(self):
        """Setup Gemini API for summary generation"""
        try:
            # Load API key from environment
            api_key = os.environ.get('GEMINI_API_KEY')
            if not api_key:
                print("❌ GEMINI_API_KEY environment variable not set")
                return
            
            genai.configure(api_key=api_key)
            self.gemini_model = genai.GenerativeModel('gemini-flash-latest')
            print("✅ Gemini Flash model configured successfully")
        except Exception as e:
            print(f"❌ Error setting up Gemini: {e}")

# FAISS Vector Database with Semantic Search
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
            print("🤖 Attempting to load SentenceTransformer model 'all-MiniLM-L6-v2'...")
        
            # Add device specification and disable gradients to save memory
            import torch
            torch.set_grad_enabled(False)
        
            # Try loading with explicit CPU device and reduced memory usage
            self.embedding_model = SentenceTransformer(
                'all-MiniLM-L6-v2',
                device='cpu',  # Force CPU usage
                cache_folder=str(self.config.faiss_cache_dir / 'sentence_transformers')
            )
        
            print("✅ Loaded SentenceTransformer model for semantic search")
            print(f"   - Device: cpu")
            print(f"   - Max sequence length: {self.embedding_model.max_seq_length}")
        
            # Test the model with a small sample
            test_embedding = self.embedding_model.encode(["test"])
            print(f"   - Test embedding shape: {test_embedding.shape}")
            print(f" - Embedding dimension: {test_embedding.shape[1]}")
        
        except Exception as e:
            print(f"❌ Failed to load embedding model: {e}")
            print(f"📋 Full traceback:")
            import traceback
            traceback.print_exc()
            self.embedding_model = None
    
    def _load_faiss_index(self):
        """Load FAISS index and metadata from Hugging Face Hub"""
        try:
            print(f"📂 Downloading FAISS files from Hugging Face Hub...")
            print(f"   Repository: {self.config.hf_repo_id}")
            
            # Import huggingface_hub here to avoid dependency issues
            from huggingface_hub import hf_hub_download
            
            # Download files from Hugging Face
            print("📥 Downloading faiss.index...")
            index_path = hf_hub_download(
                repo_id=self.config.hf_repo_id,
                filename=self.config.hf_files["index"],
                cache_dir=str(self.config.faiss_cache_dir),
                force_download=False  # Use cache if available
            )
            
            print("📥 Downloading metadata.pkl...")
            metadata_path = hf_hub_download(
                repo_id=self.config.hf_repo_id,
                filename=self.config.hf_files["metadata"],
                cache_dir=str(self.config.faiss_cache_dir),
                force_download=False
            )
            
            # Update config paths
            self.config.index_file = Path(index_path)
            self.config.metadata_file = Path(metadata_path)
            
            print(f"✅ Files downloaded:")
            print(f"   - Index: {self.config.index_file}")
            print(f"   - Metadata: {self.config.metadata_file}")
            
            # Load FAISS index
            print("🔧 Loading FAISS index...")
            self.index = faiss.read_index(str(self.config.index_file))
            
            # Load metadata
            with open(self.config.metadata_file, 'rb') as f:
                data = pickle.load(f)
                self.metadata = data.get('metadata', [])
                self.documents = data.get('documents', [])
            
            print(f"✅ Successfully loaded FAISS index with {len(self.metadata)} videos")
            print(f"   - Index dimension: {self.index.d}")
            print(f"   - Total vectors: {self.index.ntotal}")
            
        except ImportError as e:
            print(f"❌ huggingface-hub not installed: {e}")
            print("   Install with: pip install huggingface-hub")
            self._setup_empty_data()
        except Exception as e:
            print(f"❌ Error loading FAISS from Hugging Face: {e}")
            print(traceback.format_exc())
            self._setup_empty_data()
    
    def _setup_empty_data(self):
        """Setup empty data structures if loading fails"""
        self.metadata = []
        self.documents = []
        self.index = None
        print("⚠️ Using empty database - upload CSV to add data")
    
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
    
        # Check if model is actually functional by testing a small encode
        model_status = "not_loaded"
        if self.embedding_model:
            try:
                # Test if model actually works
                test_result = self.embedding_model.encode(["test"])
                model_status = "ready"
            except:
                model_status = "error"
    
        return {
            "total_videos": total_videos,
            "database_path": str(self.config.faiss_cache_dir),
            "search_engine": "SentenceTransformer + Cosine Similarity",
            "status": model_status,  # Use the model_status we calculated
            "faiss_index_loaded": self.index is not None,
            "total_vectors": self.index.ntotal if self.index else 0,
            "embedding_dimension": self.index.d if self.index else 0,
            "documents_count": len(self.documents),
            "metadata_count": len(self.metadata)
        }

    def get_document_by_id(self, doc_id):
        """Get document and metadata by original ID"""
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
    
    # Check FAISS status
    faiss_status = "loaded" if vector_db.index is not None else "not_loaded"
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "environment": "production" if vector_db.config.is_render else "development",
        "total_videos": info.get("total_videos", 0),
        "faiss_status": faiss_status,
        "faiss_source": "huggingface_hub",
        "huggingface_repo": vector_db.config.hf_repo_id,
        "api_version": "1.0.0",
        "paths": {
            "faiss_cache_dir": str(vector_db.config.faiss_cache_dir),
            "is_render": vector_db.config.is_render
        }
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

#if __name__ == "__main__":
#    import uvicorn
#    
#    print("🚀 Starting Semantic Video Search API Server...")
#    print("📚 API Endpoints (all under /api):")
#    print("   GET  /api/          - API information")
#    print("   GET  /api/health    - Health check")
#    print("   POST /api/search    - Semantic search")
#    print("   POST /api/ingest    - Upload CSV file")
#    print("   GET  /api/summary/{video_id} - Get AI-generated video summary")
#    print("\n🔧 Configuration:")
#    print(f"   - Database path: {vector_db.config.faiss_db_path}")
#    print(f"   - Search engine: SentenceTransformer + Cosine Similarity")
#    print(f"   - Embedding model: all-MiniLM-L6-v2")
#    print(f"   - Gemini model: {'Configured' if vector_db.config.gemini_model else 'Not Configured'}")
#    print(f"\n🔗 API Base URL: http://localhost:8000/api")
    
#    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)