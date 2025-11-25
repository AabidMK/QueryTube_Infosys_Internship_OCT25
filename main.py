from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import chromadb
import os

app = FastAPI(title="VectorDB API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to your existing ChromaDB
client = chromadb.PersistentClient(path="C:/Users/Admin/chroma_db")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/stats")
async def get_stats():
    try:
        print("=== DEBUG: Starting get_stats ===")
        collections = client.list_collections()
        print(f"DEBUG: Found {len(collections)} collections")
        
        total_documents = 0
        collection_counts = {}
        
        for collection in collections:
            count = collection.count()
            print(f"DEBUG: Collection '{collection.name}' has {count} documents")
            total_documents += count
            collection_counts[collection.name] = count
        
        print(f"DEBUG: Total documents: {total_documents}")
        print("=== DEBUG: Ending get_stats ===")
        
        return {
            "total_documents": total_documents,
            "collections": len(collections),
            "collection_counts": collection_counts,
            "api_status": "healthy"
        }
    except Exception as e:
        print(f"DEBUG: Error occurred: {str(e)}")
        return {
            "total_documents": 0,
            "collections": 0,
            "api_status": "error",
            "error": str(e)
        }

@app.get("/api/collections")
async def get_collections():
    try:
        collections = client.list_collections()
        collection_names = [col.name for col in collections]
        return {"collections": collection_names}
    except Exception as e:
        return {"collections": [], "error": str(e)}

@app.get("/api/collections/{collection_name}/documents")
async def get_collection_documents(collection_name: str, limit: int = 100):
    try:
        collection = client.get_collection(name=collection_name)
        results = collection.get(limit=limit)
        return {
            "documents": results.get('documents', []),
            "metadatas": results.get('metadatas', []),
            "ids": results.get('ids', [])
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Collection not found: {str(e)}")

@app.post("/api/search")
async def search_documents(request: Dict[str, Any]):
    try:
        collection_name = request.get("collection_name")
        query = request.get("query")
        limit = request.get("limit", 10)
        
        collection = client.get_collection(name=collection_name)
        results = collection.query(
            query_texts=[query],
            n_results=limit
        )
        
        return {
            "results": results.get('documents', []),
            "metadatas": results.get('metadatas', []),
            "distances": results.get('distances', []),
            "ids": results.get('ids', [])
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("Starting VectorDB Backend...")
    print("Connecting to existing ChromaDB with your 620 documents and 2 collections")
    uvicorn.run(app, host="0.0.0.0", port=8002)# Create virtual environment