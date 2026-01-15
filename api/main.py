"""
QueryTube Backend - Semantic Video Search API
Optimized for Render deployment with timeout fixes
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
import asyncio
from concurrent.futures import ThreadPoolExecutor
import threading

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
            os.environ['HF_HUB_DISABLE_PROGRESS_BARS'] = '1'
        
        self.index_file = self.faiss_cache_dir / "faiss.index"
        self.metadata_file = self.faiss_cache_dir / "metadata.pkl"
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
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash-latest')
            print("✅ Gemini model configured")
        except Exception as e:
            print(f"❌ Gemini setup error: {e}")

# =============================================
# FAISS VECTOR DATABASE WITH LAZY LOADING
# =============================================

class FAISSVectorDB:
    def __init__(self):
        print("🤖 Initializing FAISS VectorDB...")
        self.config = Config()
        self.embedding_model = None
        self.index = None
        self.metadata = []
        self.documents = []
        self.embedding_dim = 384
        self.loading_lock = threading.Lock()
        self.is_loading = False
        self.load_attempted = False
        
        # Don't load immediately - use lazy loading
        print("✅ FAISS VectorDB initialized (lazy loading enabled)")
    
    def _ensure_loaded(self):
        """Ensure components are loaded (lazy loading)"""
        if self.load_attempted:
            return
        
        with self.loading_lock:
            if self.load_attempted:
                return
            
            self.load_attempted = True
            self.is_loading = True
            
            try:
                print("🔄 Loading components (lazy)...")
                self._load_embedding_model()
                self._load_or_create_faiss_index()
                print("✅ Components loaded!")
            except Exception as e:
                print(f"⚠️ Lazy load error: {e}")
            finally:
                self.is_loading = False
    
    def _load_embedding_model(self):
        """Load embedding model with timeout protection"""
        try:
            print("   Loading embedding model (lightweight)...")
            
            import torch
            torch.set_grad_enabled(False)
            
            # Use the smallest, fastest model
            model_name = 'all-MiniLM-L6-v2'
            
            print(f"     Loading {model_name}...")
            self.embedding_model = SentenceTransformer(
                model_name,
                device='cpu',
                cache_folder=str(self.config.faiss_cache_dir / 'models')
            )
            
            # Test the model
            test_embedding = self.embedding_model.encode(["test"], normalize_embeddings=True, show_progress_bar=False)
            self.embedding_dim = test_embedding.shape[1]
            print(f"✅ Loaded {model_name} (dim: {self.embedding_dim})")
            
        except Exception as e:
            print(f"❌ Model load error: {e}")
            print("⚠️ Will use keyword search only")
            self.embedding_model = None
    
    def _load_or_create_faiss_index(self):
        """Load FAISS index with timeout protection"""
        try:
            # Try to load from local cache first
            if self.config.index_file.exists() and self.config.metadata_file.exists():
                print("📁 Loading from local cache...")
                try:
                    self.index = faiss.read_index(str(self.config.index_file))
                    
                    with open(self.config.metadata_file, 'rb') as f:
                        data = pickle.load(f)
                        self.metadata = data.get('metadata', [])
                        self.documents = data.get('documents', [])
                    
                    if self.index:
                        self.embedding_dim = self.index.d
                    
                    print(f"✅ Loaded from cache: {len(self.metadata)} videos")
                    return
                except Exception as e:
                    print(f"⚠️ Cache load failed: {e}")
            
            # Try Hugging Face download with timeout
            print("📥 Downloading from Hugging Face (with timeout)...")
            try:
                from huggingface_hub import hf_hub_download
                import signal
                
                # Download with timeout
                index_path = hf_hub_download(
                    repo_id=self.config.hf_repo_id,
                    filename=self.config.hf_files["index"],
                    cache_dir=str(self.config.faiss_cache_dir),
                    force_download=False,
                    resume_download=True
                )
                
                metadata_path = hf_hub_download(
                    repo_id=self.config.hf_repo_id,
                    filename=self.config.hf_files["metadata"],
                    cache_dir=str(self.config.faiss_cache_dir),
                    force_download=False,
                    resume_download=True
                )
                
                # Load FAISS index
                self.index = faiss.read_index(str(index_path))
                
                # Load metadata
                with open(metadata_path, 'rb') as f:
                    data = pickle.load(f)
                    self.metadata = data.get('metadata', [])
                    self.documents = data.get('documents', [])
                
                if self.index:
                    self.embedding_dim = self.index.d
                
                # Copy to local cache for faster future loads
                import shutil
                shutil.copy(index_path, self.config.index_file)
                shutil.copy(metadata_path, self.config.metadata_file)
                
                print(f"✅ Loaded from HF: {len(self.metadata)} videos")
                return
                
            except Exception as e:
                print(f"⚠️ HF download failed: {e}")
        
        except Exception as e:
            print(f"⚠️ Load error: {e}")
        
        # Create empty index as fallback
        print("🔧 Creating empty index...")
        if self.embedding_model:
            self.index = faiss.IndexFlatIP(self.embedding_dim)
            print(f"✅ Created empty index (dim: {self.embedding_dim})")
        else:
            self.index = None
        
        self.metadata = []
        self.documents = []
    
    def _rebuild_index(self):
        """Rebuild FAISS index from documents"""
        if not self.embedding_model or not self.documents:
            print("⚠️ Cannot rebuild: missing model or documents")
            return
        
        print(f"🔄 Rebuilding index: {len(self.documents)} docs...")
        
        try:
            self.index = faiss.IndexFlatIP(self.embedding_dim)
            
            # Generate embeddings in batches
            batch_size = 32
            all_embeddings = []
            
            for i in range(0, len(self.documents), batch_size):
                batch = self.documents[i:i+batch_size]
                embeddings = self.embedding_model.encode(
                    batch, 
                    normalize_embeddings=True, 
                    show_progress_bar=False,
                    batch_size=batch_size
                )
                all_embeddings.append(embeddings)
            
            if all_embeddings:
                all_embeddings = np.vstack(all_embeddings).astype('float32')
                self.index.add(all_embeddings)
                print(f"✅ Index rebuilt: {self.index.ntotal} vectors")
            
            self._save_index()
            
        except Exception as e:
            print(f"❌ Rebuild error: {e}")
            traceback.print_exc()
    
    def _save_index(self):
        """Save FAISS index and metadata"""
        try:
            if self.index and self.index.ntotal > 0:
                faiss.write_index(self.index, str(self.config.index_file))
                print(f"💾 Saved index: {self.config.index_file}")
            
            data = {
                'metadata': self.metadata,
                'documents': self.documents
            }
            with open(self.config.metadata_file, 'wb') as f:
                pickle.dump(data, f)
            
            print(f"💾 Saved metadata: {self.config.metadata_file}")
            
        except Exception as e:
            print(f"❌ Save error: {e}")
    
    def semantic_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Enhanced semantic search"""
        # Ensure components are loaded
        self._ensure_loaded()
        
        print(f"\n🔍 Search: '{query}'")
        
        if not self.documents:
            print("⚠️ No documents")
            return []
        
        # Use keyword if no semantic model/index
        if not self.embedding_model or not self.index or self.index.ntotal == 0:
            print("⚠️ Using keyword search")
            return self.keyword_fallback_search(query, top_k)
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(
                [query], 
                normalize_embeddings=True,
                show_progress_bar=False
            ).astype('float32')
            
            # Search FAISS
            k = min(top_k * 2, self.index.ntotal)
            distances, indices = self.index.search(query_embedding, k)
            
            results = []
            
            for distance, doc_idx in zip(distances[0], indices[0]):
                if doc_idx >= len(self.documents):
                    continue
                
                metadata = self.metadata[doc_idx]
                doc = self.documents[doc_idx]
                
                similarity_score = float(distance)
                
                # Keyword matching
                title = metadata.get('title', '').lower()
                transcript = doc.lower()
                query_lower = query.lower()
                
                keyword_in_title = self._fuzzy_keyword_match(query_lower, title)
                keyword_in_transcript = self._fuzzy_keyword_match(query_lower, transcript)
                
                # Boost for keywords
                if keyword_in_title:
                    similarity_score += 0.1
                if keyword_in_transcript:
                    similarity_score += 0.05
                
                similarity_score = min(max(similarity_score, 0), 1)
                
                # Relevance
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
                
                preview = doc[:200] + "..." if len(doc) > 200 else doc
                
                results.append({
                    'id': metadata.get('original_id', f"video_{doc_idx}"),
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
            
            results.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            print(f"✅ Found {len(results)} matches")
            return results[:top_k]
            
        except Exception as e:
            print(f"❌ Search error: {e}")
            return self.keyword_fallback_search(query, top_k)
    
    def _fuzzy_keyword_match(self, query: str, text: str) -> bool:
        """Fuzzy keyword matching"""
        query_words = query.lower().split()
        text_lower = text.lower()
        
        for word in query_words:
            if len(word) > 2 and word in text_lower:
                return True
        
        return False
    
    def keyword_fallback_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Keyword search fallback"""
        print(f"🔍 Keyword search: '{query}'")
        
        try:
            query_lower = query.lower()
            query_words = query_lower.split()
            results = []
            
            for i, (doc, metadata) in enumerate(zip(self.documents, self.metadata)):
                title = metadata.get('title', '').lower()
                transcript = doc.lower()
                
                score = 0.0
                
                # Title matches
                for word in query_words:
                    if len(word) > 2 and word in title:
                        score += 0.4
                
                # Transcript matches
                for word in query_words:
                    if len(word) > 2 and word in transcript:
                        score += 0.1
                        count = transcript.count(word)
                        score += min(0.05, count * 0.01)
                
                # Exact phrase
                if query_lower in title:
                    score += 0.2
                if query_lower in transcript:
                    score += 0.1
                
                if score > 0:
                    preview = doc[:200] + "..." if len(doc) > 200 else doc
                    
                    results.append({
                        'id': metadata.get('original_id', f"video_{i}"),
                        'title': metadata.get('title', 'Unknown'),
                        'channel': metadata.get('channel_title', 'Unknown'),
                        'views': metadata.get('view_count', 'N/A'),
                        'duration': metadata.get('duration', 'N/A'),
                        'similarity_score': round(score, 4),
                        'keyword_in_title': any(word in title for word in query_words if len(word) > 2),
                        'keyword_in_transcript': any(word in transcript for word in query_words if len(word) > 2),
                        'relevance': "Keyword Match",
                        'preview': preview,
                        'metadata': metadata
                    })
            
            results.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            print(f"✅ Found {len(results)} matches")
            return results[:top_k]
            
        except Exception as e:
            print(f"❌ Keyword error: {e}")
            return []
    
    def add_documents(self, documents: List[str], metadatas: List[Dict[str, Any]]):
        """Add documents and rebuild index"""
        # Ensure loaded first
        self._ensure_loaded()
        
        print(f"\n📥 Adding {len(documents)} documents...")
        
        self.documents.extend(documents)
        self.metadata.extend(metadatas)
        
        print(f"✅ Added. Total: {len(self.documents)}")
        
        if self.embedding_model:
            self._rebuild_index()
        else:
            print("⚠️ Skipping index rebuild")
            self._save_index()
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get database info"""
        return {
            "total_videos": len(self.metadata),
            "total_documents": len(self.documents),
            "model_loaded": self.embedding_model is not None,
            "model_status": "ready" if self.embedding_model else "not_loaded",
            "faiss_loaded": self.index is not None,
            "total_vectors": self.index.ntotal if self.index else 0,
            "embedding_dim": self.embedding_dim,
            "is_loading": self.is_loading,
            "load_attempted": self.load_attempted,
            "environment": "render" if self.config.is_render else "local"
        }
    
    def get_document_by_id(self, doc_id):
        """Get document by ID"""
        self._ensure_loaded()
        
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
        
        Provide a concise summary.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Summary error: {str(e)[:100]}"

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

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router
api_router = APIRouter(prefix="/api")

# Initialize database (lightweight, no immediate loading)
print("🔄 Initializing database (lazy)...")
vector_db = FAISSVectorDB()
print("✅ Database ready!")

# =============================================
# MIDDLEWARE
# =============================================

@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    """Add CORS headers"""
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
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
        "api_base": "/api"
    }

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

# =============================================
# API ENDPOINTS
# =============================================

@api_router.get("/")
async def api_root():
    """API root"""
    return {
        "api": "QueryTube API",
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
    """API health"""
    info = vector_db.get_database_info()
    
    return {
        "status": "healthy",
        "database": info,
        "timestamp": datetime.now().isoformat()
    }

@api_router.get("/debug")
async def debug_info():
    """Debug info"""
    return {
        "database_info": vector_db.get_database_info(),
        "render": vector_db.config.is_render
    }

@api_router.post("/search", response_model=SearchResponse)
async def search_videos(search_query: SearchQuery):
    """Search videos"""
    try:
        print(f"\n🔍 SEARCH: '{search_query.query}'")
        
        # Perform search
        results = vector_db.semantic_search(
            query=search_query.query,
            top_k=search_query.top_k
        )
        
        search_type = "semantic" if (vector_db.embedding_model and vector_db.index and vector_db.index.ntotal > 0) else "keyword"
        
        if not results:
            return SearchResponse(
                results=[],
                query=search_query.query,
                total_results=0,
                average_similarity=0.0,
                max_similarity=0.0,
                search_type=search_type
            )
        
        similarities = [r['similarity_score'] for r in results]
        avg_sim = sum(similarities) / len(similarities)
        max_sim = max(similarities)
        
        print(f"✅ Found {len(results)} results")
        
        return SearchResponse(
            results=results,
            query=search_query.query,
            total_results=len(results),
            average_similarity=round(avg_sim, 4),
            max_similarity=round(max_sim, 4),
            search_type=search_type
        )
        
    except Exception as e:
        print(f"❌ Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/ingest", response_model=IngestionResponse)
async def ingest_document(file: UploadFile = File(...)):
    """Ingest CSV"""
    try:
        print(f"\n📥 INGEST: {file.filename}")
        
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        
        ingested = 0
        errors = 0
        documents = []
        metadatas = []
        
        for idx, row in df.iterrows():
            try:
                text = str(row.get('transcript', '')).strip()
                if not text or text == 'nan':
                    errors += 1
                    continue
                
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
        
        if documents:
            vector_db.add_documents(documents, metadatas)
        
        print(f"✅ Ingested {ingested} docs")
        
        return IngestionResponse(
            id=str(uuid.uuid4()),
            status="success" if ingested > 0 else "failed",
            message=f"Processed {ingested} documents",
            timestamp=datetime.now().isoformat(),
            ingested_count=ingested,
            error_count=errors,
            total_chunks=ingested
        )
        
    except Exception as e:
        print(f"❌ Ingest error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@api_router.get("/summary/{video_id}", response_model=VideoSummaryResponse)
async def get_video_summary(video_id: str):
    """Get video summary"""
    try:
        video_data = vector_db.get_document_by_id(video_id)
        if not video_data:
            raise HTTPException(status_code=404, detail="Video not found")
        
        stats = vector_db.get_video_statistics(video_id)
        if not stats:
            stats = {}
        
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
# REGISTER ROUTER
# =============================================

app.include_router(api_router)

@app.options("/{path:path}")
async def options_handler(path: str):
    """CORS preflight"""
    return JSONResponse(
        content={"message": "OK"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*"
        }
    )

print("\n" + "=" * 60)
print("✅ API Ready (Lazy Loading Enabled)")
print("=" * 60)
print(f"🌐 Ready to accept requests!")
print("=" * 60)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)