import requests
import json

BASE_URL = "http://localhost:8000"

def test_api():
    print("Testing VectorDB API...")
    
    # Test root endpoint
    response = requests.get(f"{BASE_URL}/")
    print("1. Root endpoint:", response.json())
    
    # Test health check
    response = requests.get(f"{BASE_URL}/health")
    print("2. Health check:", response.json())
    
    # Test ingestion
    doc_data = {
        "text": "Machine learning is a subset of artificial intelligence",
        "metadata": {"category": "AI", "author": "Test User"}
    }
    
    response = requests.post(f"{BASE_URL}/api/ingest", json=doc_data)
    print("3. Ingestion response:", response.json())
    
    # Test get documents
    response = requests.get(f"{BASE_URL}/api/documents")
    data = response.json()
    print(f"4. Get documents: {data['count']} documents found")
    
    # Test search
    search_data = {
        "query": "machine learning",
        "top_k": 3
    }
    response = requests.post(f"{BASE_URL}/api/search", json=search_data)
    print("5. Search results:", response.json())

if __name__ == "__main__":
    test_api()