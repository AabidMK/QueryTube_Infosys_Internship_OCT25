import chromadb

def search_videos_simple():
    # Initialize ChromaDB client
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_collection("youtube_videos")
    
    print(f"📊 Database contains {collection.count()} videos")
    
    # Get user query
    user_query = input("\n🔍 Enter your search query: ").strip()
    
    if not user_query:
        print("❌ Please enter a query")
        return
    
    print(f"\n🔄 Searching for: '{user_query}'")
    
    # Use ChromaDB's built-in text embedding
    results = collection.query(
        query_texts=[user_query],
        n_results=5,
        include=['metadatas', 'distances', 'documents']
    )
    
    # Display results
    print(f"\n🎯 Top 5 most relevant videos for: '{user_query}'")
    print("=" * 80)
    
    if not results['ids'][0]:
        print("❌ No results found")
        return
    
    for i, (video_id, metadata, distance) in enumerate(zip(
        results['ids'][0], 
        results['metadatas'][0], 
        results['distances'][0]
    )):
        similarity_score = 1 - distance  # Convert distance to similarity
        
        print(f"\n{i+1}. 🆔 Video ID: {video_id}")
        print(f"   📺 Title: {metadata['title']}")
        print(f"   🏢 Channel: {metadata['channel_title']}")
        print(f"   ⭐ Similarity Score: {similarity_score:.4f}")
        print(f"   👀 Views: {int(metadata['view_count']):,}")
        print("-" * 60)

if __name__ == "__main__":
    search_videos_simple()