"""
QueryTube Backend - Semantic Video Search API
Main application file with guaranteed CORS fix
"""

import faiss
from pathlib import Path
from fastapi import FastAPI, HTTPException, UploadFile, File, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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
import asyncio

# Load environment variables from .env file
load_dotenv()

print("=" * 60)
print("🚀 Starting QueryTube Semantic Search Backend")
print("=" * 60)

# =============================================
# PYDANTIC MODELS
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
# CONFIGURATION
# =============================================

class Config:
    """Configuration manager"""
    def __init__(self):
        self.is_render = os.environ.get('RENDER') is not None
        
        # Hugging Face Repository
        self.hf_repo_id = "karunya-3/faiss-video-db"
        self.hf_files = {
            "index": "faiss.index",
            "metadata": "metadata.pkl"
        }
        
        # Paths
        if self.is_render:
            self.base_dir = Path("/tmp")
            self.faiss_cache_dir = self.base_dir / "faiss_cache"
            print("🚀 Running in RENDER environment")
        else:
            self.base_dir = Path(__file__).parent
            self.faiss_cache_dir = self.base_dir / "faiss_cache"
        
        # Create directories
        os.makedirs(self.faiss_cache_dir, exist_ok=True)
        
        # Set environment variables for Render
        if self.is_render:
            os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
            os.environ['TOKENIZERS_PARALLELISM'] = 'false'
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
        
        self.index_file = None
        self.metadata_file = None
        self.gemini_model = None
        self._setup_gemini()

    def _setup_gemini(self):
        """Setup Gemini API"""
        try:
            api_key = os.environ.get('GEMINI_API_KEY')
            if not api_key:
                print("⚠️ GEMINI_API_KEY not set")
                return
            
            genai.configure(api_key=api_key)
            self.gemini_model = genai.GenerativeModel('gemini-flash-latest')
            print("✅ Gemini model configured")
        except Exception as e:
            print(f"❌ Gemini setup error: {e}")

# =============================================
# FAISS VECTOR DATABASE
# =============================================

class FAISSVectorDB:
    """FAISS-based vector database"""
    def __init__(self):
        print("🤖 Initializing FAISS VectorDB...")
        self.config = Config()
        self.embedding_model = None
        self.index = None
        self.metadata = []
        self.documents = []
        
        # Load components with error handling
        try:
            self._load_embedding_model()
            self._load_faiss_index()
            print("✅ FAISS VectorDB initialized!")
        except Exception as e:
            print(f"⚠️ Partial initialization: {e}")
    
    def _load_embedding_model(self):
        """Load embedding model"""
        try:
            import torch
            torch.set_grad_enabled(False)
            
            # Try multiple models
            models_to_try = [
                'all-MiniLM-L6-v2',
                'paraphrase-MiniLM-L3-v2',
                'all-mpnet-base-v2'
            ]
            
            for model_name in models_to_try:
                try:
                    print(f"   Trying model: {model_name}")
                    self.embedding_model = SentenceTransformer(
                        model_name,
                        device='cpu',
                        cache_folder=str(self.config.faiss_cache_dir / 'models')
                    )
                    
                    # Test the model
                    test_embedding = self.embedding_model.encode(["test"])
                    print(f"✅ Loaded {model_name}")
                    print(f"   - Dimension: {test_embedding.shape[1]}")
                    return
                    
                except Exception as e:
                    print(f"   ❌ {model_name} failed: {str(e)[:100]}")
                    continue
            
            print("⚠️ All models failed, using keyword search only")
            self.embedding_model = None
            
        except Exception as e:
            print(f"❌ Model loading failed: {e}")
            self.embedding_model = None
    
    def _load_faiss_index(self):
        """Load FAISS index from Hugging Face"""
        try:
            from huggingface_hub import hf_hub_download
            
            print(f"📥 Downloading FAISS files...")
            
            # Download index
            index_path = hf_hub_download(
                repo_id=self.config.hf_repo_id,
                filename=self.config.hf_files["index"],
                cache_dir=str(self.config.faiss_cache_dir),
                force_download=False
            )
            
            # Download metadata
            metadata_path = hf_hub_download(
                repo_id=self.config.hf_repo_id,
                filename=self.config.hf_files["metadata"],
                cache_dir=str(self.config.faiss_cache_dir),
                force_download=False
            )
            
            self.config.index_file = Path(index_path)
            self.config.metadata_file = Path(metadata_path)
            
            # Load FAISS index
            print("🔧 Loading FAISS index...")
            self.index = faiss.read_index(str(self.config.index_file))
            
            # Load metadata
            with open(self.config.metadata_file, 'rb') as f:
                data = pickle.load(f)
                self.metadata = data.get('metadata', [])
                self.documents = data.get('documents', [])
            
            print(f"✅ Loaded {len(self.metadata)} videos")
            print(f"   - Vectors: {self.index.ntotal}")
            print(f"   - Dimension: {self.index.d}")
            
        except Exception as e:
            print(f"❌ FAISS loading error: {e}")
            print("⚠️ Using empty database")
            self.metadata = []
            self.documents = []
            self.index = None
    
    def semantic_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Perform semantic search"""
        # Fallback to keyword search if no model
        if self.embedding_model is None:
            return self.keyword_fallback_search(query, top_k)
        
        if not self.documents:
            return []
        
        try:
            # Generate embeddings
            query_embedding = self.embedding_model.encode([query])
            results = []
            
            for i, (doc, metadata) in enumerate(zip(self.documents, self.metadata)):
                doc_embedding = self.embedding_model.encode([doc])
                similarity = cosine_similarity(query_embedding, doc_embedding)[0][0]
                
                # Calculate relevance
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
                
                # Keyword matches
                title = metadata.get('title', '').lower()
                transcript = doc.lower()
                query_lower = query.lower()
                
                results.append({
                    'id': metadata.get('original_id', f"video_{i}"),
                    'title': metadata.get('title', 'Unknown'),
                    'channel': metadata.get('channel_title', 'Unknown'),
                    'views': metadata.get('view_count', 'N/A'),
                    'duration': metadata.get('duration', 'N/A'),
                    'similarity_score': similarity_score,
                    'keyword_in_title': query_lower in title,
                    'keyword_in_transcript': query_lower in transcript,
                    'relevance': relevance,
                    'preview': doc[:200] + "..." if len(doc) > 200 else doc,
                    'metadata': metadata
                })
            
            # Sort and return top results
            results.sort(key=lambda x: x['similarity_score'], reverse=True)
            return results[:top_k]
            
        except Exception as e:
            print(f"❌ Semantic search error: {e}")
            return self.keyword_fallback_search(query, top_k)
    
    def keyword_fallback_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Keyword fallback search"""
        try:
            query_lower = query.lower()
            results = []
            
            for i, (doc, metadata) in enumerate(zip(self.documents, self.metadata)):
                title = metadata.get('title', '').lower()
                transcript = doc.lower()
                
                # Calculate score based on keyword matches
                score = 0.0
                if query_lower in title:
                    score += 0.5
                if query_lower in transcript:
                    score += 0.3
                    score += min(0.2, transcript.count(query_lower) * 0.05)
                
                if score > 0:
                    results.append({
                        'id': metadata.get('original_id', f"video_{i}"),
                        'title': metadata.get('title', 'Unknown'),
                        'channel': metadata.get('channel_title', 'Unknown'),
                        'views': metadata.get('view_count', 'N/A'),
                        'duration': metadata.get('duration', 'N/A'),
                        'similarity_score': score,
                        'keyword_in_title': query_lower in title,
                        'keyword_in_transcript': query_lower in transcript,
                        'relevance': "Keyword Match",
                        'preview': doc[:200] + "..." if len(doc) > 200 else doc,
                        'metadata': metadata
                    })
            
            results.sort(key=lambda x: x['similarity_score'], reverse=True)
            return results[:top_k]
            
        except Exception as e:
            print(f"❌ Keyword search error: {e}")
            return []
    
    def add_documents(self, documents: List[str], metadatas: List[Dict[str, Any]]):
        """Add documents to database"""
        self.documents.extend(documents)
        self.metadata.extend(metadatas)
        print(f"✅ Added {len(documents)} documents")
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get database info"""
        return {
            "total_videos": len(self.metadata),
            "model_loaded": self.embedding_model is not None,
            "model_status": "ready" if self.embedding_model else "not_loaded",
            "faiss_loaded": self.index is not None,
            "total_vectors": self.index.ntotal if self.index else 0,
            "documents": len(self.documents),
            "environment": "render" if self.config.is_render else "local"
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
        """Get video statistics"""
        video_data = self.get_document_by_id(doc_id)
        if not video_data:
            return None
        
        transcript = video_data['document']
        metadata = video_data['metadata']
        
        words = transcript.split()
        sentences = [s for s in transcript.split('.') if s.strip()]
        
        return {
            'id': doc_id,
            'title': metadata.get('title', 'N/A'),
            'channel': metadata.get('channel_title', 'N/A'),
            'views': metadata.get('view_count', 'N/A'),
            'duration': metadata.get('duration', 'N/A'),
            'transcript_length': len(transcript),
            'word_count': len(words),
            'sentence_count': len(sentences),
            'avg_word_length': sum(len(w) for w in words) / len(words) if words else 0,
            'avg_sentence_length': sum(len(s) for s in sentences) / len(sentences) if sentences else 0
        }

# =============================================
# HELPER FUNCTIONS
# =============================================

def generate_video_summary(model, video_data):
    """Generate summary using Gemini"""
    try:
        prompt = f"""
        Summarize this video:
        
        Title: {video_data['metadata'].get('title', 'N/A')}
        Channel: {video_data['metadata'].get('channel_title', 'N/A')}
        Views: {video_data['metadata'].get('view_count', 'N/A')}
        
        Transcript (first 3000 chars):
        {video_data['document'][:3000]}
        
        Provide a concise, informative summary.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Summary generation error: {str(e)[:100]}"

# =============================================
# FASTAPI APP WITH CORS FIX
# =============================================

# Initialize FastAPI app FIRST
app = FastAPI(
    title="QueryTube API",
    description="Semantic Video Search Engine",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware IMMEDIATELY after creating app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Create router
api_router = APIRouter(prefix="/api")

# Initialize database
print("🔄 Initializing database...")
vector_db = FAISSVectorDB()
print("✅ Database ready!")

# =============================================
# CUSTOM MIDDLEWARE FOR CORS HEADERS
# =============================================

@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    """Add CORS headers to all responses"""
    response = await call_next(request)
    
    # Add CORS headers
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Max-Age"] = "600"
    
    return response

# =============================================
# ROOT ENDPOINTS
# =============================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "QueryTube Semantic Search",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs",
        "api_base": "/api",
        "message": "Welcome to QueryTube API"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "QueryTube API"
    }

# =============================================
# API ENDPOINTS
# =============================================

@api_router.get("/")
async def api_root():
    """API root"""
    return {
        "api": "QueryTube Semantic Search API",
        "endpoints": {
            "health": "GET /api/health",
            "search": "POST /api/search",
            "upload": "POST /api/ingest",
            "summary": "GET /api/summary/{id}",
            "debug": "GET /api/debug"
        },
        "status": "operational"
    }

@api_router.get("/health")
async def api_health():
    """API health check"""
    info = vector_db.get_database_info()
    
    return {
        "status": "healthy",
        "database": info,
        "cors": "enabled",
        "timestamp": datetime.now().isoformat(),
        "environment": "production" if vector_db.config.is_render else "development"
    }

@api_router.get("/debug")
async def debug_info():
    """Debug information"""
    return {
        "database_info": vector_db.get_database_info(),
        "cors_enabled": True,
        "render_environment": vector_db.config.is_render,
        "python_version": os.sys.version,
        "total_endpoints": len(app.routes)
    }

@api_router.post("/search", response_model=SearchResponse)
async def search_videos(search_query: SearchQuery):
    """Search videos"""
    try:
        print(f"🔍 Searching for: '{search_query.query}'")
        
        results = vector_db.semantic_search(
            query=search_query.query,
            top_k=search_query.top_k
        )
        
        # Calculate stats
        if results:
            similarities = [r['similarity_score'] for r in results]
            avg_sim = sum(similarities) / len(similarities)
            max_sim = max(similarities)
        else:
            avg_sim = 0.0
            max_sim = 0.0
        
        return SearchResponse(
            results=results,
            query=search_query.query,
            total_results=len(results),
            average_similarity=round(avg_sim, 4),
            max_similarity=round(max_sim, 4),
            search_type="semantic" if vector_db.embedding_model else "keyword"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/ingest", response_model=IngestionResponse)
async def ingest_document(file: UploadFile = File(...)):
    """Ingest CSV file"""
    try:
        # Read and parse CSV
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        
        ingested = 0
        errors = 0
        documents = []
        metadatas = []
        
        # Process each row
        for idx, row in df.iterrows():
            try:
                # Extract text
                text = str(row.get('transcript', '')).strip()
                if not text:
                    errors += 1
                    continue
                
                # Extract metadata
                metadata = {
                    'original_id': str(row.get('id', f"doc_{idx}")),
                    'title': str(row.get('title', f"Video {idx}")),
                    'channel_title': str(row.get('channel_title', 'Unknown')),
                    'view_count': str(row.get('view_count', 'N/A')),
                    'duration': str(row.get('duration', 'N/A'))
                }
                
                documents.append(text)
                metadatas.append(metadata)
                ingested += 1
                
            except Exception:
                errors += 1
        
        # Add to database
        if documents:
            vector_db.add_documents(documents, metadatas)
        
        return IngestionResponse(
            id=str(uuid.uuid4()),
            status="success",
            message=f"Processed {ingested} documents",
            timestamp=datetime.now().isoformat(),
            ingested_count=ingested,
            error_count=errors,
            total_chunks=ingested
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"CSV processing error: {str(e)}")

@api_router.get("/summary/{video_id}", response_model=VideoSummaryResponse)
async def get_video_summary(video_id: str):
    """Get video summary"""
    try:
        # Get video data
        video_data = vector_db.get_document_by_id(video_id)
        if not video_data:
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Get statistics
        stats = vector_db.get_video_statistics(video_id)
        if not stats:
            stats = {}
        
        # Generate summary
        summary = "Summary not available"
        if vector_db.config.gemini_model:
            try:
                summary = generate_video_summary(vector_db.config.gemini_model, video_data)
            except Exception as e:
                summary = f"Summary error: {str(e)[:100]}"
        
        return VideoSummaryResponse(
            id=video_id,
            title=stats.get('title', 'Unknown'),
            channel=stats.get('channel', 'Unknown'),
            views=stats.get('views', 'N/A'),
            duration=stats.get('duration', 'N/A'),
            summary=summary,
            statistics=stats,
            generated_at=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =============================================
# REGISTER ROUTER AND FINAL SETUP
# =============================================

# Include API router
app.include_router(api_router)

# Add OPTIONS handler for CORS preflight
@app.options("/{path:path}")
async def options_handler(path: str):
    """Handle OPTIONS requests for CORS"""
    return JSONResponse(
        content={"message": "CORS preflight successful"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Max-Age": "600"
        }
    )

print("\n" + "=" * 60)
print("✅ API Setup Complete")
print("=" * 60)
print(f"📊 Database: {len(vector_db.metadata)} videos loaded")
print(f"🤖 Model: {'Loaded' if vector_db.embedding_model else 'Not loaded'}")
print(f"🔗 URL: https://querytube-backend-37mk.onrender.com")
print(f"📚 Docs: https://querytube-backend-37mk.onrender.com/docs")
print("=" * 60)
print("🚀 Ready to accept requests!")
print("=" * 60)

# If running directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)