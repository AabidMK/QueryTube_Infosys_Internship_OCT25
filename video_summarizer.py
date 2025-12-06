# working_summarizer.py
import chromadb
import json
from datetime import datetime
import re
import subprocess
import sys

def fix_ollama_import():
    """Fix Ollama import issues"""
    print("🔧 Fixing Ollama import...")
    
    # Try different import methods
    try:
        # Method 1: Direct import
        import ollama
        print("✅ Ollama imported successfully")
        return ollama
    except ImportError:
        print("❌ Ollama not installed. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "ollama"])
            import ollama
            print("✅ Ollama installed and imported")
            return ollama
        except:
            print("❌ Failed to install Ollama")
            return None
    except Exception as e:
        print(f"❌ Import error: {e}")
        return None

class WorkingVideoSummarizer:
    def __init__(self, collection_name="youtube_videos"):
        """
        Working video summarization system
        """
        try:
            # Initialize ChromaDB
            self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
            self.collection = self.chroma_client.get_collection(name=collection_name)
            print(f"✅ Connected to database: {self.collection.count()} videos")
            
            # Try to initialize Ollama
            self.ollama = fix_ollama_import()
            self.use_ai = self.ollama is not None
            
            if self.use_ai:
                print("✅ AI summarization available")
            else:
                print("⚠️  Using basic summarization (no AI)")
            
        except Exception as e:
            print(f"❌ Initialization error: {e}")
            self.collection = None
    
    def get_video_info(self, video_id):
        """Get video information from database"""
        try:
            result = self.collection.get(
                ids=[video_id],
                include=['metadatas']
            )
            
            if result and result['ids']:
                metadata = result['metadatas'][0]
                return {
                    'id': video_id,
                    'title': metadata.get('title', 'Unknown Title'),
                    'channel': metadata.get('channel_title', 'Unknown Channel'),
                    'transcript': metadata.get('transcript', ''),
                    'views': int(metadata.get('view_count', 0)),
                    'duration': metadata.get('duration', 'Unknown'),
                    'published': metadata.get('published_at', ''),
                    'tags': metadata.get('tags', '')
                }
            return None
        except Exception as e:
            print(f"❌ Database error: {e}")
            return None
    
    def clean_text(self, text, max_length=1500):
        """Clean and truncate text"""
        if not text:
            return ""
        
        # Fix common encoding issues
        fixes = [
            ('â€"', ' - '),
            ('â€™', "'"),
            ('â€œ', '"'),
            ('â€', '"'),
            ('â€¦', '...'),
        ]
        
        for old, new in fixes:
            text = text.replace(old, new)
        
        # Remove URLs
        text = re.sub(r'https?://\S+', '', text)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Truncate if needed
        if len(text) > max_length:
            # Try to cut at sentence end
            cut = text[:max_length].rfind('. ')
            if cut > 500:  # Make sure we have enough content
                text = text[:cut+1] + "..."
            else:
                text = text[:max_length] + "..."
        
        return text.strip()
    
    def ai_summarize(self, transcript, title):
        """Summarize using AI"""
        try:
            prompt = f"""Create a brief summary (2-3 sentences) of this YouTube video:

Title: {title}

Transcript excerpt:
{transcript}

Summary:"""
            
            response = self.ollama.chat(
                model='llama3.2',
                messages=[{'role': 'user', 'content': prompt}]
            )
            
            return response['message']['content']
        except Exception as e:
            print(f"❌ AI summarization failed: {e}")
            return None
    
    def basic_summarize(self, transcript, title):
        """Basic extractive summarization"""
        print("📝 Creating basic summary...")
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', transcript)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        if not sentences:
            return "Could not extract summary from transcript."
        
        # Take important sentences (first, and any with keywords)
        summary_sentences = []
        
        # Always include first sentence
        if sentences:
            summary_sentences.append(sentences[0])
        
        # Look for keywords in remaining sentences
        keywords = ['explain', 'discover', 'found', 'mystery', 'secret', 
                   'scientist', 'research', 'reveal', 'show', 'prove']
        
        for sentence in sentences[1:]:
            if any(keyword in sentence.lower() for keyword in keywords):
                if sentence not in summary_sentences:
                    summary_sentences.append(sentence)
                    if len(summary_sentences) >= 3:
                        break
        
        # If we don't have enough, add more sentences
        if len(summary_sentences) < 2 and len(sentences) > 1:
            summary_sentences.append(sentences[-1])  # Last sentence
        
        return ' '.join(summary_sentences) + '.'
    
    def create_summary(self, video_id):
        """Create summary for video"""
        print(f"\n📹 Processing: {video_id}")
        print("=" * 50)
        
        # Get video data
        video = self.get_video_info(video_id)
        if not video:
            print(f"❌ Video not found: {video_id}")
            return None
        
        print(f"✅ {video['title']}")
        print(f"   📺 {video['channel']}")
        print(f"   ⏱️  {video['duration']}")
        print(f"   👁️  {video['views']:,} views")
        
        # Clean transcript
        transcript = self.clean_text(video['transcript'])
        if not transcript:
            print("❌ No transcript available")
            return None
        
        print(f"   📄 Transcript: {len(transcript)} characters")
        
        # Generate summary
        if self.use_ai:
            print("🤖 Using AI for summarization...")
            summary = self.ai_summarize(transcript, video['title'])
            if not summary:
                print("⚠️  AI failed, using basic method")
                summary = self.basic_summarize(transcript, video['title'])
        else:
            summary = self.basic_summarize(transcript, video['title'])
        
        if not summary:
            print("❌ Failed to generate summary")
            return None
        
        # Create result
        result = {
            'video_id': video_id,
            'title': video['title'],
            'channel': video['channel'],
            'duration': video['duration'],
            'views': video['views'],
            'published': video.get('published', ''),
            'summary': summary,
            'used_ai': self.use_ai,
            'created_at': datetime.now().isoformat(),
            'transcript_excerpt': transcript[:300] + "..." if len(transcript) > 300 else transcript
        }
        
        return result
    
    def show_summary(self, result):
        """Display summary"""
        print("\n" + "=" * 70)
        print("📋 SUMMARY REPORT")
        print("=" * 70)
        print(f"🎬 {result['title']}")
        print(f"👤 {result['channel']}")
        print(f"⏱️  {result['duration']} | 👁️  {result['views']:,} views")
        print(f"🆔 {result['video_id']}")
        if result.get('published'):
            print(f"📅 {result['published']}")
        print("=" * 70)
        
        print(f"\n📝 {'AI ' if result['used_ai'] else ''}SUMMARY:")
        print("-" * 40)
        print(result['summary'])
        
        print(f"\n📄 TRANSCRIPT EXCERPT:")
        print("-" * 40)
        print(result['transcript_excerpt'])
        print("=" * 70)
    
    def save_summary(self, result):
        """Save summary to file"""
        filename = f"summary_{result['video_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Saved to: {filename}")
            return filename
        except Exception as e:
            print(f"❌ Save failed: {e}")
            return None

def test_system():
    """Test the system"""
    print("🧪 Testing system...")
    
    # Test database
    try:
        client = chromadb.PersistentClient(path="./chroma_db")
        collection = client.get_collection("youtube_videos")
        count = collection.count()
        print(f"✅ Database: {count} videos")
        
        # Test with a known video
        test_id = "t8txtQkhMcY"
        result = collection.get(ids=[test_id], include=['metadatas'])
        if result and result['ids']:
            print(f"✅ Test video found: {result['metadatas'][0]['title'][:50]}...")
        else:
            print("❌ Test video not found")
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
    
    # Test Ollama
    try:
        import ollama
        models = ollama.list()
        print(f"✅ Ollama: {len(models.get('models', []))} models available")
    except:
        print("⚠️  Ollama not available")

def main():
    """Main program"""
    print("=" * 60)
    print("🎬 WORKING VIDEO SUMMARIZER")
    print("=" * 60)
    
    # Run system test
    test_system()
    
    # Initialize
    summarizer = WorkingVideoSummarizer()
    
    if not summarizer.collection:
        print("❌ Failed to initialize. Exiting.")
        return
    
    # Example videos
    examples = [
        ("t8txtQkhMcY", "Mystery Mountain"),
        ("mmIidOoHCfs", "Pirate Treasure"),
        ("CvTsL-WcrgQ", "Killer Waves"),
        ("H8SAmnrwSfk", "Terrifying Snakes"),
    ]
    
    print("\n📋 Examples:")
    for i, (vid, desc) in enumerate(examples, 1):
        print(f"  {i}. {vid} - {desc}")
    
    while True:
        print("\n" + "=" * 50)
        print("Menu:")
        print("  1. Summarize by ID")
        print("  2. Try example")
        print("  3. Exit")
        
        choice = input("\nChoice (1-3): ").strip()
        
        if choice == "1":
            video_id = input("Video ID: ").strip()
            if video_id:
                result = summarizer.create_summary(video_id)
                if result:
                    summarizer.show_summary(result)
                    save = input("\n💾 Save? (y/n): ").strip().lower()
                    if save == 'y':
                        summarizer.save_summary(result)
        
        elif choice == "2":
            print("\nExamples:")
            for i, (vid, desc) in enumerate(examples, 1):
                print(f"  {i}. {vid} - {desc}")
            
            try:
                num = int(input("\nSelect (1-4): ").strip())
                if 1 <= num <= len(examples):
                    video_id = examples[num-1][0]
                    result = summarizer.create_summary(video_id)
                    if result:
                        summarizer.show_summary(result)
                        save = input("\n💾 Save? (y/n): ").strip().lower()
                        if save == 'y':
                            summarizer.save_summary(result)
                else:
                    print("❌ Invalid number")
            except:
                print("❌ Invalid input")
        
        elif choice == "3":
            print("\n👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice")

def quick_run(video_id):
    """Quick run for command line"""
    print(f"\n🔍 Summarizing: {video_id}")
    
    summarizer = WorkingVideoSummarizer()
    result = summarizer.create_summary(video_id)
    
    if result:
        print(f"\n📺 {result['title']}")
        print(f"👤 {result['channel']}")
        print(f"\n📝 Summary:\n{result['summary']}")
        
        # Auto-save
        filename = summarizer.save_summary(result)
        if filename:
            print(f"\n✅ Saved: {filename}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Command line: python working_summarizer.py <video_id>
        quick_run(sys.argv[1])
    else:
        main()