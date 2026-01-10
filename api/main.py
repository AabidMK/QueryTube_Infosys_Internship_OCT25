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
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create router with API prefix
api_router = APIRouter(prefix="/api")

# Initialize FastAPI app
app = FastAPI(
    title="Semantic Video Search API",
    description="API for semantic search and analysis of video content using AI embeddings",
    version="1.0.0"
)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "QueryTube Semantic Search API",
        "status": "running",
        "version": "1.0.0",
        "api_base": "/api"
    }

# Add CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================
# PYDANTIC MODELS FOR REQUEST/RESPONSE VALIDATION
# =============================================

class SearchQuery(BaseModel):
    """Model for search request body"""
    query: str
    top_k: int = 5

class SearchResult(BaseModel):
    """Model for individual search result"""
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
    """Model for search response"""
    results: List[SearchResult]
    query: str
    total_results: int
    average_similarity: float
    max_similarity: float
    search_type: str

class IngestionResponse(BaseModel):
    """Model for ingestion response"""
    id: str
    status: str
    message: str
    timestamp: str
    ingested_count: int
    error_count: int
    total_chunks: int

class VideoSummaryResponse(BaseModel):
    """Model for video summary response"""
    id: str
    title: str
    channel: str
    views: Any
    duration: str
    summary: str
    statistics: Dict[str, Any]
    generated_at: str

# =============================================
# CONFIGURATION CLASS
# =============================================

class Config:
    """Configuration manager for environment-specific settings"""
    def __init__(self):
        # Check if running on Render
        self.is_render = os.environ.get('RENDER') is not None
        
        # Hugging Face Repository Info
        self.hf_repo_id = "karunya-3/faiss-video-db"
        self.hf_files = {
            "index": "faiss.index",
            "metadata": "metadata.pkl"
        }
        
        # Set paths based on environment
        if self.is_render:
            # Render production paths - use /tmp for better compatibility
            self.base_dir = Path("/tmp")
            self.faiss_cache_dir = self.base_dir / "faiss_cache"
            print("🚀 Running in RENDER environment")
            print(f"📂 Cache directory: {self.faiss_cache_dir}")
            
            # Set environment variables for better performance on Render
            os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
            os.environ['TOKENIZERS_PARALLELISM'] = 'false'
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
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
                print("⚠️ GEMINI_API_KEY environment variable not set")
                print("   Summary generation will be disabled")
                return
            
            genai.configure(api_key=api_key)
            self.gemini_model = genai.GenerativeModel('gemini-flash-latest')
            print("✅ Gemini Flash model configured successfully")
        except Exception as e:
            print(f"❌ Error setting up Gemini: {e}")

# =============================================
# FAISS VECTOR DATABASE CLASS
# =============================================

class FAISSVectorDB:
    """FAISS-based vector database with semantic search capabilities"""
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
        """Load SentenceTransformer model for semantic search with retry logic"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"🤖 Attempt {attempt + 1}/{max_retries} to load SentenceTransformer model...")
                
                import torch
                
                # Clear CUDA cache if available
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                
                # Force CPU on Render
                device = 'cpu' if self.config.is_render else 'cpu'
                
                # Disable gradients to save memory
                torch.set_grad_enabled(False)
                
                # Try different models if primary fails
                if attempt == 0:
                    model_name = 'all-MiniLM-L6-v2'  # Primary model
                elif attempt == 1:
                    model_name = 'paraphrase-MiniLM-L3-v2'  # Smaller model
                else:
                    model_name = 'all-MiniLM-L6-v2'  # Try primary again
                
                print(f"   Loading model: {model_name}")
                print(f"   Device: {device}")
                
                # Load the model
                self.embedding_model = SentenceTransformer(
                    model_name,
                    device=device,
                    cache_folder=str(self.config.faiss_cache_dir / 'sentence_transformers')
                )
                
                # Test the model with a simple embedding
                test_text = ["test embedding for verification"]
                test_embedding = self.embedding_model.encode(
                    test_text, 
                    show_progress_bar=False,
                    normalize_embeddings=True
                )
                
                print(f"✅ Successfully loaded embedding model")
                print(f"   - Model: {model_name}")
                print(f"   - Device: {device}")
                print(f"   - Embedding dimension: {test_embedding.shape[1]}")
                
                return
                
            except Exception as e:
                print(f"❌ Attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    print("⚠️ Could not load embedding model. Using keyword fallback search.")
                    print("📋 Last error details:")
                    traceback.print_exc()
                    self.embedding_model = None
                else:
                    import time
                    time.sleep(2)  # Wait before retry
    
    def _load_faiss_index(self):
        """Load FAISS index and metadata from Hugging Face Hub"""
        try:
            print(f"📂 Downloading FAISS files from Hugging Face Hub...")
            print(f"   Repository: {self.config.hf_repo_id}")
            
            # Import huggingface_hub
            from huggingface_hub import hf_hub_download
            
            # Download files from Hugging Face
            print("📥 Downloading faiss.index...")
            index_path = hf_hub_download(
                repo_id=self.config.hf_repo_id,
                filename=self.config.hf_files["index"],
                cache_dir=str(self.config.faiss_cache_dir),
                force_download=False,
                local_files_only=False
            )
            
            print("📥 Downloading metadata.pkl...")
            metadata_path = hf_hub_download(
                repo_id=self.config.hf_repo_id,
                filename=self.config.hf_files["metadata"],
                cache_dir=str(self.config.faiss_cache_dir),
                force_download=False,
                local_files_only=False
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
            print("📖 Loading metadata...")
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
            print("📋 Traceback:")
            traceback.print_exc()
            self._setup_empty_data()
    
    def _setup_empty_data(self):
        """Setup empty data structures if loading fails"""
        self.metadata = []
        self.documents = []
        self.index = None
        print("⚠️ Using empty database - upload CSV to add data")
    
    def semantic_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Perform semantic search using SentenceTransformer embeddings
        Falls back to keyword search if embedding model fails
        """
        # Check if embedding model is available
        if self.embedding_model is None:
            print("⚠️ Embedding model not available, using keyword fallback")
            return self.keyword_fallback_search(query, top_k)
        
        if not self.documents:
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(
                [query], 
                show_progress_bar=False,
                normalize_embeddings=True
            )
            
            results = []
            
            # Process each document
            for i, (doc, metadata) in enumerate(zip(self.documents, self.metadata)):
                # Generate document embedding
                doc_embedding = self.embedding_model.encode(
                    [doc], 
                    show_progress_bar=False,
                    normalize_embeddings=True
                )
                
                # Calculate cosine similarity
                similarity = cosine_similarity(query_embedding, doc_embedding)[0][0]
                
                # Check for keyword matches
                title = metadata.get('title', '').lower()
                transcript_lower = doc.lower()
                query_lower = query.lower()
                
                keyword_in_title = query_lower in title
                keyword_in_transcript = query_lower in transcript_lower
                
                # Determine relevance level based on similarity score
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
            print(f"❌ Semantic search error: {e}, falling back to keyword search")
            return self.keyword_fallback_search(query, top_k)
    
    def keyword_fallback_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Fallback keyword search when embedding model is unavailable
        Uses simple text matching with scoring
        """
        try:
            query_lower = query.lower()
            results = []
            
            for i, (doc, metadata) in enumerate(zip(self.documents, self.metadata)):
                title = metadata.get('title', '').lower()
                transcript_lower = doc.lower()
                
                # Simple keyword matching score
                score = 0.0
                if query_lower in title:
                    score += 0.5
                if query_lower in transcript_lower:
                    score += 0.3
                    # Bonus for multiple occurrences
                    score += min(0.2, transcript_lower.count(query_lower) * 0.05)
                
                # Only include results with some match
                if score > 0:
                    preview = doc[:200] + "..." if len(doc) > 200 else doc
                    
                    results.append({
                        'id': metadata.get('original_id', f"video_{i}"),
                        'title': metadata.get('title', 'Unknown Title'),
                        'channel': metadata.get('channel_title', 'Unknown Channel'),
                        'views': metadata.get('view_count', 'N/A'),
                        'duration': metadata.get('duration', 'N/A'),
                        'similarity_score': score,
                        'keyword_in_title': query_lower in title,
                        'keyword_in_transcript': query_lower in transcript_lower,
                        'relevance': "Keyword Match",
                        'preview': preview,
                        'metadata': metadata
                    })
            
            # Sort by score
            results.sort(key=lambda x: x['similarity_score'], reverse=True)
            return results[:top_k]
            
        except Exception as e:
            print(f"❌ Keyword fallback search error: {e}")
            return []
    
    def add_documents(self, documents: List[str], metadatas: List[Dict[str, Any]]):
        """Add documents to the in-memory database (for demo purposes)"""
        self.documents.extend(documents)
        self.metadata.extend(metadatas)
        print(f"✅ Added {len(documents)} documents to in-memory database")
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get comprehensive database information"""
        total_videos = len(self.metadata)
        
        # Check model status
        model_status = "not_loaded"
        if self.embedding_model:
            try:
                # Test if model actually works
                test_result = self.embedding_model.encode(["test"])
                model_status = "ready"
            except Exception as e:
                model_status = f"error: {str(e)[:50]}"
        
        return {
            "total_videos": total_videos,
            "database_path": str(self.config.faiss_cache_dir),
            "search_engine": "SentenceTransformer + Cosine Similarity",
            "model_status": model_status,
            "faiss_index_loaded": self.index is not None,
            "total_vectors": self.index.ntotal if self.index else 0,
            "embedding_dimension": self.index.d if self.index else 0,
            "documents_count": len(self.documents),
            "metadata_count": len(self.metadata),
            "is_render": self.config.is_render
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
        
        # Calculate statistics
        words = transcript.split()
        sentences = [s for s in transcript.split('.') if s.strip()]
        
        stats = {
            'id': doc_id,
            'title': metadata.get('title', 'N/A'),
            'channel': metadata.get('channel_title', 'N/A'),
            'views': metadata.get('view_count', 'N/A'),
            'duration': metadata.get('duration', 'N/A'),
            'transcript_length': len(transcript),
            'word_count': len(words),
            'sentence_count': len(sentences),
            'avg_word_length': sum(len(word) for word in words) / len(words) if words else 0,
            'avg_sentence_length': sum(len(s) for s in sentences) / len(sentences) if sentences else 0
        }
        
        return stats

# =============================================
# HELPER FUNCTIONS
# =============================================

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

# =============================================
# INITIALIZE DATABASE
# =============================================

print("=" * 60)
print("🚀 Starting QueryTube Semantic Search Backend")
print("=" * 60)

vector_db = FAISSVectorDB()

print("=" * 60)
print("✅ Backend initialization complete")
print("=" * 60)

# =============================================
# API ENDPOINTS
# =============================================

@api_router.get("/")
async def api_root():
    """API root endpoint"""
    return {
        "message": "Semantic Video Search API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "health": "GET /api/health",
            "search": "POST /api/search",
            "ingest": "POST /api/ingest",
            "summary": "GET /api/summary/{video_id}",
            "debug": "GET /api/debug/model"
        },
        "search_engine": "Semantic Search with SentenceTransformer"
    }

@api_router.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    info = vector_db.get_database_info()
    
    # Check FAISS status
    faiss_status = "loaded" if vector_db.index is not None else "not_loaded"
    
    return {
        "status": "healthy" if info["model_status"] == "ready" else "degraded",
        "timestamp": datetime.now().isoformat(),
        "environment": "production" if vector_db.config.is_render else "development",
        "total_videos": info.get("total_videos", 0),
        "model_status": info.get("model_status", "unknown"),
        "faiss_status": faiss_status,
        "faiss_source": "huggingface_hub",
        "huggingface_repo": vector_db.config.hf_repo_id,
        "api_version": "1.0.0",
        "service": "QueryTube Semantic Search"
    }

@api_router.get("/debug/model")
async def debug_model():
    """Debug endpoint to check model status"""
    try:
        model_status = "not_loaded"
        error_message = None
        test_success = False
        test_shape = None
        
        if vector_db.embedding_model:
            try:
                # Test the model
                test_result = vector_db.embedding_model.encode(["test sentence for debugging"])
                model_status = "ready"
                test_shape = test_result.shape
                test_success = True
            except Exception as e:
                model_status = "error"
                error_message = str(e)
        else:
            error_message = "Model not initialized"
        
        return {
            "model_loaded": vector_db.embedding_model is not None,
            "model_status": model_status,
            "error": error_message,
            "test_successful": test_success,
            "test_shape": str(test_shape) if test_shape else None,
            "total_documents": len(vector_db.documents),
            "total_metadata": len(vector_db.metadata),
            "environment": "render" if vector_db.config.is_render else "local",
            "cache_dir": str(vector_db.config.faiss_cache_dir),
            "cache_exists": os.path.exists(vector_db.config.faiss_cache_dir),
            "python_version": os.sys.version,
            "memory_info": {
                "available_mb": os.sys.getsizeof(vector_db) // 1024 // 1024,
                "total_vectors": vector_db.index.ntotal if vector_db.index else 0
            }
        }
    except Exception as e:
        return {"error": str(e)}

@api_router.post("/search", response_model=SearchResponse)
async def search_videos(search_query: SearchQuery):
    """Search videos using semantic or keyword search"""
    try:
        print(f"🔍 Search request: '{search_query.query}' (top_k={search_query.top_k})")
        
        # Perform search
        results = vector_db.semantic_search(
            query=search_query.query,
            top_k=search_query.top_k
        )
        
        # Determine search type
        search_type = "semantic" if vector_db.embedding_model else "keyword"
        
        if not results:
            return SearchResponse(
                results=[],
                query=search_query.query,
                total_results=0,
                average_similarity=0.0,
                max_similarity=0.0,
                search_type=search_type
            )
        
        # Calculate statistics
        similarities = [r['similarity_score'] for r in results]
        avg_similarity = sum(similarities) / len(similarities)
        max_similarity = max(similarities)
        
        print(f"✅ Found {len(results)} results (type: {search_type})")
        
        return SearchResponse(
            results=results,
            query=search_query.query,
            total_results=len(results),
            average_similarity=round(avg_similarity, 4),
            max_similarity=round(max_similarity, 4),
            search_type=search_type
        )
        
    except Exception as e:
        print(f"❌ Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@api_router.post("/ingest", response_model=IngestionResponse)
async def ingest_document(file: UploadFile = File(...)):
    """
    Ingest documents from a CSV file
    CSV must have columns including 'transcript'
    """
    try:
        print(f"📥 Starting ingestion: {file.filename}")
        
        # Validate file type
        if not file.filename.lower().endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV")
        
        # Read file
        contents = await file.read()
        
        if len(contents) == 0:
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Parse CSV
        try:
            df = pd.read_csv(io.BytesIO(contents))
            print(f"✅ CSV read successfully. Shape: {df.shape}")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid CSV format: {str(e)}")
        
        # Check required columns
        if 'transcript' not in df.columns:
            raise HTTPException(status_code=400, detail="CSV must contain 'transcript' column")
        
        # Determine available columns
        text_column = 'transcript'
        id_column = 'id' if 'id' in df.columns else None
        title_column = 'title' if 'title' in df.columns else 'title_cleaned' if 'title_cleaned' in df.columns else None
        channel_column = 'channel_title' if 'channel_title' in df.columns else 'channel' if 'channel' in df.columns else None
        views_column = 'view_count' if 'view_count' in df.columns else 'views' if 'views' in df.columns else None
        duration_column = 'duration' if 'duration' in df.columns else 'duration_seconds' if 'duration_seconds' in df.columns else None
        
        ingested_count = 0
        error_count = 0
        documents = []
        metadatas = []
        
        # Process each row
        for index, row in df.iterrows():
            try:
                text = str(row[text_column]).strip()
                if not text or text.lower() in ['nan', 'none', '']:
                    error_count += 1
                    continue
                
                # Extract metadata
                metadata = {
                    'original_id': str(row[id_column]) if id_column and pd.notna(row.get(id_column)) else f"doc_{index}_{uuid.uuid4().hex[:8]}",
                    'title': str(row[title_column]) if title_column and pd.notna(row.get(title_column)) else f"Document {index}",
                    'channel_title': str(row[channel_column]) if channel_column and pd.notna(row.get(channel_column)) else "Unknown Channel",
                    'view_count': int(row[views_column]) if views_column and pd.notna(row.get(views_column)) and str(row[views_column]).replace('.','').isdigit() else "N/A",
                    'duration': str(row[duration_column]) if duration_column and pd.notna(row.get(duration_column)) else "N/A"
                }
                
                # Add to collections
                documents.append(text)
                metadatas.append(metadata)
                ingested_count += 1
                
                if ingested_count % 100 == 0:
                    print(f"✅ Processed {ingested_count} rows...")
                
            except Exception as e:
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
        print(f"❌ Ingestion error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@api_router.get("/summary/{video_id}", response_model=VideoSummaryResponse)
async def get_video_summary(video_id: str):
    """Get AI-generated summary for a specific video"""
    try:
        print(f"📝 Generating summary for video: {video_id}")
        
        # Get video data
        video_data = vector_db.get_document_by_id(video_id)
        if not video_data:
            raise HTTPException(status_code=404, detail=f"Video with ID '{video_id}' not found")
        
        # Get video statistics
        statistics = vector_db.get_video_statistics(video_id)
        if not statistics:
            raise HTTPException(status_code=404, detail=f"Could not retrieve statistics for video '{video_id}'")
        
        # Generate AI summary
        summary = "Summary generation not available"
        if vector_db.config.gemini_model:
            try:
                summary = generate_video_summary(vector_db.config.gemini_model, video_data)
            except Exception as e:
                summary = f"❌ Error generating AI summary: {str(e)[:100]}"
        else:
            summary = "⚠️ Gemini API not configured - cannot generate AI summary"
        
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

# =============================================
# REGISTER ROUTER AND FINAL SETUP
# =============================================

# Include the router with /api prefix
app.include_router(api_router)

print("\n" + "=" * 60)
print("✅ API Endpoints Registered:")
print("=" * 60)
print("   GET  /api/                - API information")
print("   GET  /api/health          - Health check")
print("   GET  /api/debug/model     - Debug model status")
print("   POST /api/search          - Semantic search")
print("   POST /api/ingest          - Upload CSV file")
print("   GET  /api/summary/{id}    - Get video summary")
print("\n🔗 Primary URL: https://querytube-backend-37mk.onrender.com")
print("🔗 API Base URL: https://querytube-backend-37mk.onrender.com/api")
print("📚 Documentation: https://querytube-backend-37mk.onrender.com/docs")
print("=" * 60)
print("🚀 Server is ready to accept requests!")
print("=" * 60)

# Note: Render runs the app using gunicorn command specified in render.yaml
# The app will be served at the PORT environment variable