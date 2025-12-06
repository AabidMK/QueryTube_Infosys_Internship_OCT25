# query_chromadb_final.py
import chromadb
import numpy as np

class VideoVectorDB:
    def __init__(self, collection_name="youtube_videos"):
        try:
            self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
            self.collection = self.chroma_client.get_collection(name=collection_name)
            self.count = self.collection.count()
            print(f"✅ Connected to collection '{collection_name}' with {self.count} videos")
        except Exception as e:
            print(f"❌ Error connecting to ChromaDB: {e}")
            print("Make sure you've run setup_chromadb.py first")
            self.collection = None
            self.count = 0
    
    def is_connected(self):
        return self.collection is not None
    
    def get_video_by_id(self, video_id, include_embedding=True):
        """Retrieve a specific video by ID"""
        if not self.is_connected():
            print("❌ Not connected to database")
            return None
        
        try:
            # Use include parameter to control what we get back
            if include_embedding:
                result = self.collection.get(ids=[video_id], include=['embeddings', 'metadatas'])
            else:
                result = self.collection.get(ids=[video_id], include=['metadatas'])
            
            if result and result['ids'] and len(result['ids']) > 0:
                video_data = {
                    'id': result['ids'][0],
                    'metadata': result['metadatas'][0] if result.get('metadatas') else {},
                }
                
                # Handle embeddings
                if include_embedding and result.get('embeddings') and len(result['embeddings']) > 0:
                    embedding = result['embeddings'][0]
                    if embedding is not None and len(embedding) > 0:
                        video_data['embedding'] = embedding
                    else:
                        video_data['embedding'] = None
                else:
                    video_data['embedding'] = None
                
                return video_data
            else:
                print(f"❌ Video with ID '{video_id}' not found")
                return None
                
        except Exception as e:
            print(f"❌ Error retrieving video {video_id}: {e}")
            return None
    
    def search_similar_to_video(self, video_id, n_results=5):
        """Find videos similar to a specific video"""
        if not self.is_connected():
            return None
        
        print(f"🔍 Finding videos similar to: {video_id}")
        
        # First get the video WITH embedding
        video = self.get_video_by_id(video_id, include_embedding=True)
        if not video:
            print(f"❌ Cannot find video {video_id}")
            return None
        
        # If no embedding, try to use text search instead
        if not video.get('embedding'):
            print(f"⚠️  No embedding found for {video_id}, using text search instead")
            title = video['metadata'].get('title', '')
            if title:
                return self.search_by_text(title, n_results=n_results)
            else:
                print(f"❌ Cannot find similar videos - no embedding or title")
                return None
        
        try:
            # Query for similar videos
            results = self.collection.query(
                query_embeddings=[video['embedding']],
                n_results=min(n_results + 2, self.count)  # Get extra in case original is in results
            )
            
            # Filter results
            filtered_results = []
            if results and results['ids'] and len(results['ids'][0]) > 0:
                for i, (vid_id, distance, metadata) in enumerate(zip(
                    results['ids'][0], 
                    results['distances'][0], 
                    results['metadatas'][0]
                )):
                    # Skip the original video and any duplicates
                    if vid_id != video_id and vid_id not in [r['id'] for r in filtered_results]:
                        filtered_results.append({
                            'id': vid_id,
                            'title': metadata.get('title', 'Unknown'),
                            'channel': metadata.get('channel_title', 'Unknown'),
                            'views': int(metadata.get('view_count', 0)),
                            'duration': metadata.get('duration', 'Unknown'),
                            'similarity': 1 - distance,
                            'excerpt': (metadata.get('transcript', '')[:200] + "...") if metadata.get('transcript', '') else ""
                        })
                    
                    # Stop when we have enough results
                    if len(filtered_results) >= n_results:
                        break
                
                print(f"✅ Found {len(filtered_results)} similar videos")
                return filtered_results
            else:
                print("❌ No similar videos found")
                return None
                
        except Exception as e:
            print(f"❌ Error in similarity search: {e}")
            return None
    
    def search_by_text(self, query_text, n_results=5):
        """Search by text in metadata (title, transcript)"""
        if not self.is_connected():
            print("Not connected to database")
            return None
            
        print(f"🔍 Searching for: '{query_text}'")
        
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=min(n_results, self.count)
            )
            
            return self._format_results(results, max_results=n_results)
        except Exception as e:
            print(f"❌ Error in text search: {e}")
            return None
    
    def search_similar_to_text(self, text, n_results=5):
        """Find videos similar to text using text embeddings"""
        if not self.is_connected():
            return None
            
        print(f"🔍 Finding videos similar to text: '{text}'")
        
        try:
            results = self.collection.query(
                query_texts=[text],
                n_results=min(n_results, self.count)
            )
            
            return self._format_results(results, max_results=n_results)
        except Exception as e:
            print(f"❌ Error searching for similar videos: {e}")
            return None
    
    def _format_results(self, results, max_results=5):
        """Format query results for display"""
        if not results or not results.get('ids') or len(results['ids'][0]) == 0:
            return []
        
        formatted = []
        for i, (vid_id, distance, metadata) in enumerate(zip(
            results['ids'][0][:max_results], 
            results['distances'][0][:max_results], 
            results['metadatas'][0][:max_results]
        )):
            formatted.append({
                'id': vid_id,
                'title': metadata.get('title', 'Unknown'),
                'channel': metadata.get('channel_title', 'Unknown'),
                'views': int(metadata.get('view_count', 0)),
                'duration': metadata.get('duration', 'Unknown'),
                'similarity': 1 - distance if distance is not None else None,
                'excerpt': (metadata.get('transcript', '')[:200] + "...") if metadata.get('transcript', '') else ""
            })
        
        return formatted
    
    def print_video_details(self, video):
        """Print detailed video information"""
        if not video:
            print("No video data provided")
            return
        
        print("\n" + "="*80)
        print("VIDEO DETAILS")
        print("="*80)
        print(f"ID: {video['id']}")
        print(f"Title: {video['metadata'].get('title', 'Unknown')}")
        print(f"Channel: {video['metadata'].get('channel_title', 'Unknown')}")
        print(f"Views: {int(video['metadata'].get('view_count', 0)):,}")
        print(f"Duration: {video['metadata'].get('duration', 'Unknown')}")
        print(f"Published: {video['metadata'].get('published_at', 'N/A')}")
        print(f"Has embedding: {'Yes' if video.get('embedding') else 'No'}")
        print("="*80)
    
    def print_results(self, results, title="Results"):
        """Print formatted results"""
        if not results:
            print("No results found")
            return
        
        print(f"\n{title}:")
        print("="*80)
        
        for i, item in enumerate(results, 1):
            print(f"\n{i}. {item['title']}")
            print(f"   ID: {item['id']}")
            print(f"   Channel: {item['channel']}")
            print(f"   Views: {item['views']:,}")
            print(f"   Duration: {item['duration']}")
            if item.get('similarity') is not None:
                print(f"   Similarity: {item['similarity']:.3f}")
            if item.get('excerpt'):
                print(f"   Excerpt: {item['excerpt']}")
        
        print("="*80)

# Test function
def test_system():
    """Test the entire system"""
    print("🧪 YOUTUBE VIDEO VECTOR DATABASE TEST")
    print("=" * 60)
    
    db = VideoVectorDB()
    
    if not db.is_connected():
        print("Failed to connect to database")
        return
    
    # Test IDs
    test_videos = [
        ("mmIidOoHCfs", "$138 Million Pirate Treasure"),
        ("t8txtQkhMcY", "Tibet Mountain Mystery"),
        ("CvTsL-WcrgQ", "Killer Waves"),
        ("H8SAmnrwSfk", "Snakes")
    ]
    
    for video_id, description in test_videos:
        print(f"\n{'='*60}")
        print(f"TEST: {description} (ID: {video_id})")
        print('='*60)
        
        # Get video
        video = db.get_video_by_id(video_id, include_embedding=True)
        
        if video:
            db.print_video_details(video)
            
            # Find similar
            print(f"\n🔍 Finding similar videos...")
            similar = db.search_similar_to_video(video_id, n_results=3)
            
            if similar:
                db.print_results(similar, f"Videos similar to: {video['metadata'].get('title', 'Unknown')}")
            else:
                print("No similar videos found")
        else:
            print(f"❌ Could not retrieve video {video_id}")

def interactive_query():
    """Interactive query interface"""
    db = VideoVectorDB()
    
    if not db.is_connected():
        return
    
    while True:
        print("\n" + "="*60)
        print("YOUTUBE VIDEO VECTOR DATABASE")
        print("="*60)
        print(f"Total videos: {db.count}")
        print("\nOptions:")
        print("1. Search by keyword")
        print("2. Find similar videos")
        print("3. Get video by ID")
        print("4. List similar videos to text")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            query = input("Enter search keyword: ").strip()
            if query:
                results = db.search_by_text(query, n_results=10)
                db.print_results(results, f"Search results for: '{query}'")
            else:
                print("Please enter a search term")
        
        elif choice == "2":
            video_id = input("Enter video ID: ").strip()
            if video_id:
                video = db.get_video_by_id(video_id, include_embedding=False)
                if video:
                    db.print_video_details(video)
                    
                    results = db.search_similar_to_video(video_id, n_results=5)
                    if results:
                        db.print_results(results, f"Videos similar to: {video['metadata'].get('title', 'Unknown')}")
        
        elif choice == "3":
            video_id = input("Enter video ID: ").strip()
            if video_id:
                video = db.get_video_by_id(video_id, include_embedding=True)
                if video:
                    db.print_video_details(video)
        
        elif choice == "4":
            text = input("Enter text: ").strip()
            if text:
                results = db.search_similar_to_text(text, n_results=5)
                db.print_results(results, f"Videos similar to text: '{text}'")
        
        elif choice == "5":
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    # Run test first
    test_system()
    
    # Then run interactive query
    print("\n" + "="*60)
    print("STARTING INTERACTIVE QUERY")
    print("="*60)
    
    run_interactive = input("\nRun interactive query? (y/n): ").strip().lower()
    if run_interactive == 'y':
        interactive_query()