# query_system.py
import chromadb
import numpy as np
from sentence_transformers import SentenceTransformer
import pandas as pd

class VideoSearchSystem:
    def __init__(self, collection_name="youtube_videos"):
        """
        Initialize the video search system
        """
        try:
            # Initialize ChromaDB client
            self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
            self.collection = self.chroma_client.get_collection(name=collection_name)
            self.count = self.collection.count()
            print(f"✅ Connected to video database with {self.count} videos")
            
            # Initialize the embedding model (same as used for videos)
            # Based on 384 dimensions, likely 'all-MiniLM-L6-v2'
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            print("✅ Loaded embedding model: all-MiniLM-L6-v2")
            
        except Exception as e:
            print(f"❌ Error initializing system: {e}")
            self.collection = None
            self.embedding_model = None
    
    def is_ready(self):
        """Check if system is ready"""
        return self.collection is not None and self.embedding_model is not None
    
    def query_to_embedding(self, query_text):
        """
        Convert user query to embedding vector
        """
        if not self.embedding_model:
            print("❌ Embedding model not loaded")
            return None
        
        try:
            # Encode the query to get embedding
            embedding = self.embedding_model.encode(query_text)
            print(f"✅ Converted query to {len(embedding)}-dimensional embedding")
            return embedding.tolist()  # Convert numpy array to list
        except Exception as e:
            print(f"❌ Error converting query to embedding: {e}")
            return None
    
    def search_similar_videos(self, query_embedding, n_results=5):
        """
        Search for similar videos using query embedding
        """
        if not self.collection:
            print("❌ Database not connected")
            return None
        
        try:
            # Perform similarity search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=min(n_results, self.count)
            )
            
            return results
        except Exception as e:
            print(f"❌ Error searching videos: {e}")
            return None
    
    def format_results(self, search_results):
        """
        Format search results into required output format
        """
        if not search_results or not search_results['ids']:
            return []
        
        formatted_results = []
        for i, (video_id, distance, metadata) in enumerate(zip(
            search_results['ids'][0],
            search_results['distances'][0],
            search_results['metadatas'][0]
        )):
            # Convert distance to similarity score (higher is more similar)
            similarity_score = 1 - distance
            
            formatted_results.append({
                'video_id': video_id,
                'title': metadata.get('title', 'Unknown'),
                'channel_name': metadata.get('channel_title', 'Unknown'),
                'similarity_score': round(similarity_score, 4)
            })
        
        return formatted_results
    
    def display_results(self, query, results):
        """
        Display search results in a clean format
        """
        print(f"\n🔍 SEARCH RESULTS for: '{query}'")
        print("=" * 100)
        print(f"{'Rank':<5} {'Video ID':<15} {'Similarity':<12} {'Channel':<20} {'Title'}")
        print("-" * 100)
        
        for i, result in enumerate(results, 1):
            print(f"{i:<5} {result['video_id']:<15} {result['similarity_score']:<12.4f} "
                  f"{result['channel_name'][:18]:<20} {result['title'][:50]}...")
        print("=" * 100)
    
    def search_videos_by_query(self, user_query, n_results=5):
        """
        Complete pipeline: query → embedding → search → results
        """
        if not self.is_ready():
            print("❌ System not ready. Please check initialization.")
            return None
        
        print(f"\n📝 User Query: '{user_query}'")
        
        # Step 1: Convert query to embedding
        query_embedding = self.query_to_embedding(user_query)
        if query_embedding is None:
            print("❌ Failed to convert query to embedding")
            return None
        
        # Step 2: Search for similar videos
        search_results = self.search_similar_videos(query_embedding, n_results=n_results)
        if search_results is None:
            print("❌ Failed to search videos")
            return None
        
        # Step 3: Format results
        formatted_results = self.format_results(search_results)
        
        if not formatted_results:
            print("❌ No results found")
            return None
        
        # Step 4: Display results
        self.display_results(user_query, formatted_results)
        
        return formatted_results

# Interactive search interface
def interactive_search():
    """Interactive search interface for users"""
    print("=" * 60)
    print("🎬 YOUTUBE VIDEO SEARCH SYSTEM")
    print("=" * 60)
    print("Enter queries to find relevant videos")
    print("Type 'exit' to quit\n")
    
    # Initialize the search system
    search_system = VideoSearchSystem()
    
    if not search_system.is_ready():
        print("Failed to initialize search system. Exiting.")
        return
    
    while True:
        # Get user query
        user_query = input("\n🔍 Enter your search query: ").strip()
        
        if user_query.lower() in ['exit', 'quit', 'q']:
            print("Goodbye!")
            break
        
        if not user_query:
            print("Please enter a query")
            continue
        
        # Perform search
        results = search_system.search_videos_by_query(user_query, n_results=5)
        
        if results:
            # Option to save results
            save_choice = input("\n💾 Save results to file? (y/n): ").strip().lower()
            if save_choice == 'y':
                save_results_to_file(user_query, results)

def save_results_to_file(query, results, filename="search_results.json"):
    """Save search results to a JSON file"""
    import json
    from datetime import datetime
    
    save_data = {
        'query': query,
        'timestamp': datetime.now().isoformat(),
        'results': results
    }
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
        print(f"✅ Results saved to {filename}")
    except Exception as e:
        print(f"❌ Error saving results: {e}")

# Batch search function
def batch_search(queries):
    """Search multiple queries at once"""
    search_system = VideoSearchSystem()
    
    if not search_system.is_ready():
        return
    
    all_results = {}
    
    for query in queries:
        print(f"\n{'='*60}")
        results = search_system.search_videos_by_query(query, n_results=5)
        if results:
            all_results[query] = results
    
    return all_results

# Example usage
if __name__ == "__main__":
    # Run interactive search by default
    interactive_search()
    
    # Alternatively, run batch search with example queries
    # example_queries = [
    #     "mysterious places on Earth",
    #     "ancient treasures found",
    #     "science discoveries 2025",
    #     "ocean exploration",
    #     "desert mysteries"
    # ]
    # batch_search(example_queries)