VectorDB Ingestion API (FastAPI + ChromaDB) Setup and Testing Guide

This guide covers setting up and testing the ingestion API defined in main.py.

1. Setup Instructions

Install Dependencies:
You will need Python 3.8+ installed. Create a virtual environment and install the required packages:

# Create a virtual environment (optional but recommended)
python3 -m venv venv
# Activate the environment (macOS/Linux)
source venv/bin/activate
# Activate the environment (Windows)
.\venv\Scripts\activate

# Install the required Python packages
pip install fastapi uvicorn pydantic chromadb


Run the Server:
Start the FastAPI application. It will typically run on http://127.0.0.1:8000.

uvicorn main:app --reload


(Leave this terminal running to keep the server live.)

2. Testing with cURL (Terminal)

Open a new terminal window and use the following commands.

Test 1: Successful Ingestion (POST request)

This command sends a batch of two documents to the /ingest endpoint, creating a collection named product_docs.

curl -X POST '[http://127.0.0.1:8000/ingest](http://127.0.0.1:8000/ingest)' \
-H 'Content-Type: application/json' \
-d '{
  "collection_name": "product_docs",
  "documents": [
    {
      "content": "The new X1 model features a 12-hour battery life and fast-charging capability.",
      "doc_id": "doc_x1_001",
      "metadata": {"source": "manual", "date": "2024-05-01"}
    },
    {
      "content": "Our service agreement covers all parts and labor for 3 years.",
      "doc_id": "doc_warranty_002",
      "metadata": {"source": "legal"}
    }
  ]
}'


Test 2: Verification (GET request)

Verify that the two documents were successfully added to the product_docs collection.

curl '[http://127.0.0.1:8000/collection_count/product_docs](http://127.0.0.1:8000/collection_count/product_docs)'


Expected Output: {"collection_name":"product_docs","count":2}

3. Testing with Postman (or FastAPI's built-in Docs)

Option A: Postman Configuration

Method and URL:

Method: POST

URL: http://127.0.0.1:8000/ingest

Headers:

Set Content-Type to application/json.

Body:

Select the Body tab, choose raw, and set the format to JSON.

Paste the following JSON payload:

{
  "collection_name": "user_feedback",
  "documents": [
    {
      "content": "The UI is intuitive, but the save button placement is confusing.",
      "doc_id": "feedback_001",
      "metadata": {"priority": "medium"}
    }
  ]
}


Send: Click Send. You should receive a 201 Created status and a success message confirming 1 document was ingested.

Option B: FastAPI Interactive Docs

FastAPI automatically generates interactive documentation. While the server is running, open your browser and navigate to:

http://127.0.0.1:8000/docs

Find the /ingest POST endpoint and click "Try it out".

Modify the example request body (or use the one provided in the cURL example).

Click "Execute" to test the ingestion directly from the browser.