import pickle
import os
import google.generativeai as genai
from datetime import datetime
import json
import faiss


# ADD THIS FUNCTION TO LOAD .env FILE
def load_env_file():
    """Load environment variables from .env file"""
    try:
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        print("✅ Loaded .env file successfully")
        return True
    except FileNotFoundError:
        print("❌ .env file not found")
        return False
    except Exception as e:
        print(f"❌ Error loading .env file: {e}")
        return False

# Configure Gemini API
def setup_gemini():
    """Setup Gemini API with your API key"""
    try:
        # First load the .env file
        if not load_env_file():
            return None
        
        # Now get the API key from environment
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("❌ GEMINI_API_KEY environment variable not set")
            print("💡 Make sure your .env file contains: GEMINI_API_KEY=your_actual_key")
            return None
        
        print(f"✅ Found Gemini API key (length: {len(api_key)})")
        genai.configure(api_key=api_key)
        
        # Use gemini-flash model
        model = genai.GenerativeModel('gemini-flash-latest')            

        print("✅ Gemini Flash model configured successfully")
        return model
    except Exception as e:
        print(f"❌ Error setting up Gemini: {e}")
        return None

# ... THE REST OF YOUR CODE REMAINS EXACTLY THE SAME ...
def generate_video_summary(model, video_data):
    """Generate summary using Gemini Flash model"""
    try:
        prompt = f"""
        Please analyze this video data and provide a comprehensive summary in the following format:
        
        **Video Summary**
        
        **Title:** [Video Title]
        **Channel:** [Channel Name]
        **Views:** [View Count]
        
        **Key Insights:**
        - Provide 3-5 key insights about the video content
        - Focus on main topics discussed
        - Highlight interesting patterns or themes
        
        **Content Analysis:**
        - Summarize the main content in 2-3 paragraphs
        - Identify the primary purpose of the video
        - Note any unique or standout elements
        
        **Transcript Highlights:**
        - Extract 2-3 notable quotes or important segments
        - Keep them concise and meaningful
        
        Video Data:
        Title: {video_data['metadata'].get('title', 'N/A')}
        Channel: {video_data['metadata'].get('channel_title', 'N/A')}
        Views: {video_data['metadata'].get('view_count', 'N/A')}
        Duration: {video_data['metadata'].get('duration', 'N/A')}
        
        Transcript:
        {video_data['document'][:4000]}  # Limit transcript length for API
        
        Please provide a well-structured, insightful summary that captures the essence of this video.
        """
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"❌ Error generating summary: {e}"

class FAISSVectorDB:
    def __init__(self, db_path="./faiss_videos_db"):
        self.db_path = db_path
        self.index_file = os.path.join(db_path, "faiss.index")
        self.metadata_file = os.path.join(db_path, "metadata.pkl")
        self.index = None
        self.metadata = []
        self.documents = []
        
        self._load_index()
    
    def _load_index(self):
        """Load FAISS index and metadata"""
        try:
            if os.path.exists(self.index_file) and os.path.exists(self.metadata_file):
                self.index = faiss.read_index(self.index_file)
                with open(self.metadata_file, 'rb') as f:
                    data = pickle.load(f)
                    self.metadata = data.get('metadata', [])
                    self.documents = data.get('documents', [])
                print(f"✅ Loaded FAISS index with {len(self.metadata)} items")
            else:
                print("❌ FAISS index not found. Please run vector.py first.")
        except Exception as e:
            print(f"❌ Error loading FAISS index: {e}")
    
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
        """Get basic statistics for a video"""
        video_data = self.get_document_by_id(doc_id)
        if not video_data:
            return None
        
        transcript = video_data['document']
        metadata = video_data['metadata']
        
        stats = {
            'id': doc_id,
            'title': metadata.get('title', 'N/A'),
            'channel': metadata.get('channel_title', 'N/A'),
            'views': metadata.get('view_count', 'N/A'),
            'duration': metadata.get('duration', 'N/A'),
            'transcript_length': len(transcript),
            'word_count': len(transcript.split()),
            'sentence_count': len([s for s in transcript.split('.') if s.strip()]),
            'avg_word_length': sum(len(word) for word in transcript.split()) / len(transcript.split()) if transcript.split() else 0
        }
        
        return stats

def interactive_video_summary():
    """Interactive video summary interface using Gemini Flash"""
    
    print("📊 FAISS VIDEO DATABASE - AI SUMMARY GENERATOR")
    print("=" * 50)
    
    # Setup Gemini model
    print("🔄 Setting up Gemini Flash model...")
    model = setup_gemini()
    if model is None:
        print("❌ Cannot proceed without Gemini API configuration")
        return
    
    # Load FAISS database
    print("🔄 Loading FAISS database...")
    faiss_db = FAISSVectorDB("./faiss_videos_db")
    
    if faiss_db.index is None:
        print("❌ Could not load FAISS database. Please run vector.py first.")
        return
    
    # Load metadata mapping for additional info
    metadata_mapping = None
    if os.path.exists("metadata_mapping.pkl"):
        with open("metadata_mapping.pkl", 'rb') as f:
            metadata_mapping = pickle.load(f)
    
    while True:
        print("\n" + "="*50)
        print("🎬 VIDEO SUMMARY GENERATOR")
        print("="*50)
        print("1. 📝 Generate AI Summary for Video")
        print("2. 📊 Show Video Statistics")
        print("3. 🔍 Find Video ID (List some videos)")
        print("4. 🚪 Exit")
        print("-"*50)
        
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == '1':
            # Generate AI summary
            doc_id = input("Enter Video ID: ").strip()
            if not doc_id:
                print("❌ Please enter a Video ID")
                continue
            
            print(f"\n🔍 Searching for video ID: {doc_id}...")
            video_data = faiss_db.get_document_by_id(doc_id)
            
            if video_data:
                print(f"✅ Video found!")
                print(f"\n📋 BASIC VIDEO INFO:")
                print(f"   📹 ID: {video_data['id']}")
                print(f"   📺 Title: {video_data['metadata'].get('title', 'N/A')}")
                print(f"   🏢 Channel: {video_data['metadata'].get('channel_title', 'N/A')}")
                print(f"   👀 Views: {video_data['metadata'].get('view_count', 'N/A')}")
                print(f"   ⏱️ Duration: {video_data['metadata'].get('duration', 'N/A')}")
                print(f"   📄 Transcript length: {len(video_data['document'])} characters")
                
                print(f"\n🤖 Generating AI summary with Gemini Flash...")
                print("⏳ This may take a few seconds...")
                
                summary = generate_video_summary(model, video_data)
                
                print("\n" + "="*80)
                print("🎯 AI-GENERATED VIDEO SUMMARY")
                print("="*80)
                print(summary)
                print("="*80)
                
                # Ask if user wants to save summary
                save_choice = input("\n💾 Save this summary to file? (y/n): ").strip().lower()
                if save_choice in ['y', 'yes']:
                    filename = f"video_summary_{doc_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(f"Video Summary for ID: {doc_id}\n")
                        f.write(f"Title: {video_data['metadata'].get('title', 'N/A')}\n")
                        f.write(f"Channel: {video_data['metadata'].get('channel_title', 'N/A')}\n")
                        f.write(f"Generated: {datetime.now().isoformat()}\n")
                        f.write("="*50 + "\n")
                        f.write(summary)
                    print(f"✅ Summary saved to {filename}")
                
            else:
                print(f"❌ Video with ID '{doc_id}' not found")
                print("💡 Use option 3 to find available Video IDs")
        
        elif choice == '2':
            # Show video statistics
            doc_id = input("Enter Video ID: ").strip()
            if not doc_id:
                print("❌ Please enter a Video ID")
                continue
            
            stats = faiss_db.get_video_statistics(doc_id)
            if stats:
                print(f"\n📊 VIDEO STATISTICS:")
                print(f"   📹 ID: {stats['id']}")
                print(f"   📺 Title: {stats['title']}")
                print(f"   🏢 Channel: {stats['channel']}")
                print(f"   👀 Views: {stats['views']}")
                print(f"   ⏱️ Duration: {stats['duration']}")
                print(f"   📄 Transcript Length: {stats['transcript_length']} characters")
                print(f"   🔤 Word Count: {stats['word_count']} words")
                print(f"   📝 Sentence Count: {stats['sentence_count']} sentences")
                print(f"   📏 Average Word Length: {stats['avg_word_length']:.1f} characters")
                
                # Additional insights
                if stats['word_count'] > 0:
                    reading_time = stats['word_count'] / 200  # Average reading speed
                    print(f"   ⏰ Estimated Reading Time: {reading_time:.1f} minutes")
            else:
                print(f"❌ Video with ID '{doc_id}' not found")
        
        elif choice == '3':
            # List some videos to help user find IDs
            limit = input("How many videos to list? (default 5): ").strip()
            try:
                limit = int(limit) if limit else 5
            except:
                limit = 5
            
            print(f"\n📋 SAMPLE VIDEOS (showing {limit}):")
            print("-" * 80)
            
            sample_count = min(limit, len(faiss_db.metadata))
            for i in range(sample_count):
                metadata = faiss_db.metadata[i]
                document = faiss_db.documents[i]
                print(f"{i+1}. 📹 ID: {metadata.get('original_id', 'N/A')}")
                print(f"   📺 Title: {metadata.get('title', 'N/A')}")
                print(f"   🏢 Channel: {metadata.get('channel_title', 'N/A')}")
                print(f"   👀 Views: {metadata.get('view_count', 'N/A')}")
                print(f"   📄 Preview: {document[:80]}...")
                print("-" * 80)
        
        elif choice == '4':
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please enter 1-4.")
        
        # Ask if user wants to continue
        if choice != '4':
            continue_analysis = input("\nContinue with another video? (y/n): ").strip().lower()
            if continue_analysis not in ['y', 'yes']:
                print("👋 Goodbye!")
                break

if __name__ == "__main__":
    interactive_video_summary()