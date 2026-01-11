"""
QueryTube Backend - Semantic Video Search API
Enhanced search functionality with better debugging
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
import re

# Load environment variables
load_dotenv()

print("=" * 60)
print("🚀 Starting QueryTube Semantic Search Backend")
print("=" * 60)

# =============================================
# PYDANTIC MODELS
# =============================================

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

class VideoSummaryResponse(BaseModel):
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
# FAISS VECTOR DATABASE WITH ENHANCED SEARCH
# =============================================

class FAISSVectorDB:
    def __init__(self):
        print("🤖 Initializing FAISS VectorDB with Enhanced Search...")
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
        """Load embedding model with multiple retries"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"   Attempt {attempt + 1}/{max_retries} to load embedding model...")
                
                import torch
                torch.set_grad_enabled(False)
                
                # Try different models
                models_to_try = [
                    'all-MiniLM-L6-v2',
                    'paraphrase-MiniLM-L3-v2',
                    'all-mpnet-base-v2'
                ]
                
                for model_name in models_to_try:
                    try:
                        print(f"     Trying model: {model_name}")
                        self.embedding_model = SentenceTransformer(
                            model_name,
                            device='cpu',
                            cache_folder=str(self.config.faiss_cache_dir / 'models')
                        )
                        
                        # Test the model
                        test_embedding = self.embedding_model.encode(["test"], normalize_embeddings=True)
                        print(f"✅ Loaded {model_name}")
                        print(f"     - Dimension: {test_embedding.shape[1]}")
                        return
                        
                    except Exception as e:
                        print(f"     ❌ {model_name} failed: {str(e)[:100]}")
                        continue
                
                print("⚠️ All models failed, using keyword search only")
                self.embedding_model = None
                return
                
            except Exception as e:
                print(f"❌ Attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    print("⚠️ Using keyword search only")
                    self.embedding_model = None
    
    def _load_faiss_index(self):
        """Load FAISS index from Hugging Face"""
        try:
            from huggingface_hub import hf_hub_download
            
            print(f"📥 Downloading FAISS files from Hugging Face...")
            
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
            
            # Log some sample titles for debugging
            print("\n📊 Sample video titles:")
            for i, meta in enumerate(self.metadata[:5]):
                print(f"   {i+1}. {meta.get('title', 'Unknown')[:50]}...")
            
        except Exception as e:
            print(f"❌ FAISS loading error: {e}")
            print("⚠️ Using empty database")
            self.metadata = []
            self.documents = []
            self.index = None
    
    def semantic_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Enhanced semantic search with better similarity scoring"""
        print(f"\n🔍 Starting semantic search for: '{query}'")
        
        # Fallback to keyword search if no model
        if self.embedding_model is None:
            print("⚠️ Embedding model not available, using keyword fallback")
            return self.keyword_fallback_search(query, top_k)
        
        if not self.documents:
            print("⚠️ No documents in database")
            return []
        
        try:
            # Generate query embedding with normalization
            print(f"   Generating query embedding...")
            query_embedding = self.embedding_model.encode([query], normalize_embeddings=True)
            
            results = []
            
            print(f"   Processing {len(self.documents)} documents...")
            
            for i, (doc, metadata) in enumerate(zip(self.documents, self.metadata)):
                # Generate document embedding
                doc_embedding = self.embedding_model.encode([doc], normalize_embeddings=True)
                
                # Calculate cosine similarity
                similarity = cosine_similarity(query_embedding, doc_embedding)[0][0]
                
                # Enhanced similarity scoring
                similarity_score = float(similarity)
                
                # Check for keyword matches with fuzzy matching
                title = metadata.get('title', '').lower()
                transcript = doc.lower()
                query_lower = query.lower()
                
                # Fuzzy keyword matching
                keyword_in_title = self._fuzzy_keyword_match(query_lower, title)
                keyword_in_transcript = self._fuzzy_keyword_match(query_lower, transcript)
                
                # Boost score for keyword matches
                if keyword_in_title:
                    similarity_score += 0.1
                if keyword_in_transcript:
                    similarity_score += 0.05
                
                # Ensure score is within [0, 1]
                similarity_score = min(max(similarity_score, 0), 1)
                
                # Determine relevance level
                if similarity_score >= 0.7:
                    relevance = "Highly Relevant"
                elif similarity_score >= 0.5:
                    relevance = "Very Relevant"
                elif similarity_score >= 0.3:
                    relevance = "Relevant"
                elif similarity_score >= 0.1:
                    relevance = "Somewhat Relevant"
                else:
                    relevance = "Low Relevance"
                
                # Create preview snippet
                preview = doc[:200] + "..." if len(doc) > 200 else doc
                
                results.append({
                    'id': metadata.get('original_id', f"video_{i}"),
                    'title': metadata.get('title', 'Unknown'),
                    'channel': metadata.get('channel_title', 'Unknown'),
                    'views': metadata.get('view_count', 'N/A'),
                    'duration': metadata.get('duration', 'N/A'),
                    'similarity_score': round(similarity_score, 4),
                    'keyword_in_title': keyword_in_title,
                    'keyword_in_transcript': keyword_in_transcript,
                    'relevance': relevance,
                    'preview': preview,
                    'metadata': metadata
                })
            
            # Sort by similarity score (highest first)
            results.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            print(f"✅ Found {len(results)} potential matches")
            if results:
                print(f"   Top score: {results[0]['similarity_score']}")
                print(f"   Top title: {results[0]['title'][:50]}...")
            
            return results[:top_k]
            
        except Exception as e:
            print(f"❌ Semantic search error: {e}")
            return self.keyword_fallback_search(query, top_k)
    
    def _fuzzy_keyword_match(self, query: str, text: str) -> bool:
        """Fuzzy keyword matching"""
        # Split query into words
        query_words = query.lower().split()
        text_lower = text.lower()
        
        # Check if any query word is in text
        for word in query_words:
            if len(word) > 2 and word in text_lower:
                return True
        
        # Check for partial matches
        for word in query_words:
            if len(word) > 3:
                for i in range(len(text_lower) - len(word) + 1):
                    if text_lower[i:i+len(word)] == word:
                        return True
        
        return False
    
    def keyword_fallback_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Enhanced keyword search with better scoring"""
        print(f"🔍 Starting keyword search for: '{query}'")
        
        try:
            query_lower = query.lower()
            query_words = query_lower.split()
            results = []
            
            print(f"   Searching through {len(self.documents)} documents...")
            
            for i, (doc, metadata) in enumerate(zip(self.documents, self.metadata)):
                title = metadata.get('title', '').lower()
                transcript = doc.lower()
                
                # Calculate score based on keyword matches
                score = 0.0
                
                # Title matches get highest weight
                for word in query_words:
                    if len(word) > 2 and word in title:
                        score += 0.4
                
                # Transcript matches
                for word in query_words:
                    if len(word) > 2 and word in transcript:
                        score += 0.1
                        # Bonus for multiple occurrences
                        count = transcript.count(word)
                        score += min(0.05, count * 0.01)
                
                # Exact phrase match bonus
                if query_lower in title:
                    score += 0.2
                if query_lower in transcript:
                    score += 0.1
                
                # Boost for shorter, more precise queries
                if len(query_words) == 1 and len(query_words[0]) > 3:
                    score *= 1.2
                
                if score > 0:
                    # Create preview snippet
                    preview = doc[:200] + "..." if len(doc) > 200 else doc
                    
                    results.append({
                        'id': metadata.get('original_id', f"video_{i}"),
                        'title': metadata.get('title', 'Unknown'),
                        'channel': metadata.get('channel_title', 'Unknown'),
                        'views': metadata.get('view_count', 'N/A'),
                        'duration': metadata.get('duration', 'N/A'),
                        'similarity_score': round(score, 4),
                        'keyword_in_title': any(word in title for word in query_words),
                        'keyword_in_transcript': any(word in transcript for word in query_words),
                        'relevance': "Keyword Match",
                        'preview': preview,
                        'metadata': metadata
                    })
            
            # Sort by score
            results.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            print(f"✅ Found {len(results)} keyword matches")
            if results:
                print(f"   Top score: {results[0]['similarity_score']}")
                print(f"   Top title: {results[0]['title'][:50]}...")
            
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
# FASTAPI APP
# =============================================

app = FastAPI(
    title="QueryTube API",
    description="Semantic Video Search Engine",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
        "status": "operational",
        "version": "1.0.0"
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
        "environment": "production" if vector_db.config.is_render else "development",
        "api_version": "1.0.0"
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
    """Search videos with enhanced semantic search"""
    try:
        print(f"\n" + "="*50)
        print(f"🔍 SEARCH REQUEST: '{search_query.query}' (top_k={search_query.top_k})")
        print("="*50)
        
        # Perform search
        results = vector_db.semantic_search(
            query=search_query.query,
            top_k=search_query.top_k
        )
        
        # Determine search type
        search_type = "semantic" if vector_db.embedding_model else "keyword"
        
        if not results:
            print(f"❌ No results found for: '{search_query.query}'")
            print("="*50)
            
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
        avg_sim = sum(similarities) / len(similarities)
        max_sim = max(similarities)
        
        print(f"\n📊 SEARCH RESULTS:")
        print(f"   - Total matches: {len(results)}")
        print(f"   - Search type: {search_type}")
        print(f"   - Avg similarity: {avg_sim:.4f}")
        print(f"   - Max similarity: {max_sim:.4f}")
        
        # Log top results
        for i, result in enumerate(results[:3]):
            print(f"\n   Top {i+1}:")
            print(f"     Title: {result['title'][:50]}...")
            print(f"     Score: {result['similarity_score']:.4f}")
            print(f"     Relevance: {result['relevance']}")
            print(f"     Keyword in title: {result['keyword_in_title']}")
            print(f"     Keyword in transcript: {result['keyword_in_transcript']}")
        
        print("="*50)
        
        return SearchResponse(
            results=results,
            query=search_query.query,
            total_results=len(results),
            average_similarity=round(avg_sim, 4),
            max_similarity=round(max_sim, 4),
            search_type=search_type
        )
        
    except Exception as e:
        print(f"❌ Search error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

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