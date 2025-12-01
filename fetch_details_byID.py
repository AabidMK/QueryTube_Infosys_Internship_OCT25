import chromadb

# --- Configuration (MUST match your saving script) ---
VECTOR_DB_PATH = './chroma_db'
COLLECTION_NAME = 'video_analysis_collection'

# --- 1. Initialize ChromaDB Client and Collection ---
try:
    client = chromadb.PersistentClient(path=VECTOR_DB_PATH)
    collection = client.get_collection(name=COLLECTION_NAME)
    print(f"Collection '{COLLECTION_NAME}' loaded successfully.")
    
except Exception as e:
    print(f"❌ Error loading collection: {e}")
    # Exit if connection fails
    exit() 

# --- 2. Define the ID and Fetch Data ---
video_id_to_fetch = 't8txtqkhmcy' 

results = collection.get(
    ids=[video_id_to_fetch],
    include=['embeddings', 'documents', 'metadatas']
)

# --- 3. Display All Fetched Details ---
if results['ids']:
    # Get the metadata dictionary for easier access
    metadata = results['metadatas'][0]
    
    print("\n✅ Successfully fetched ALL video data by ID:")
    
    print(f"Video ID: **{results['ids'][0]}**")
    print(f"Title: **{metadata['title']}**")
    print(f"Channel: **{metadata['channel_title']}**")
    
    # Display the two columns you were missing
    print(f"View Count: **{metadata['view_count']}**")
    print(f"Duration: **{metadata['duration']}**")

    print("\n--- Additional Data Stored ---")
    print(f"Transcript Snippet: {results['documents'][0][:100]}...")
    print(f"Embedding Vector Length: {len(results['embeddings'][0])}")
else:
    print(f"❌ Video ID {video_id_to_fetch} not found.")