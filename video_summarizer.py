# video_summarizer_fixed.py
import chromadb
import requests
import json
import time
import os
import sys
from typing import Optional, Tuple

def find_chroma_db():
    """Automatically find the ChromaDB directory"""
    # Check the Saved_db directory
    saved_db_path = "../Saved_db/chroma_db"
    if os.path.exists(saved_db_path):
        print(f"✅ Found ChromaDB at: {saved_db_path}")
        return saved_db_path
    
    # Alternative paths to check
    possible_paths = [
        "../Saved_db/chroma_db",  # Your actual location
        "../chroma_db",           # Parent directory
        "./chroma_db",            # Current directory
        "../../chroma_db"         # Grandparent directory
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"✅ Found ChromaDB at: {path}")
            return path
    
    print("❌ Could not find ChromaDB directory in any expected location.")
    print("💡 Expected locations:")
    print("   - ../Saved_db/chroma_db")
    print("   - ../chroma_db") 
    print("   - ./chroma_db")
    return None

class VideoSummarizer:
    def __init__(self, chroma_db_path: str = None):
        if chroma_db_path is None:
            chroma_db_path = find_chroma_db()
            if chroma_db_path is None:
                print("\n🚨 Please specify the ChromaDB path manually:")
                manual_path = input("Enter full path to chroma_db directory: ").strip()
                if manual_path and os.path.exists(manual_path):
                    chroma_db_path = manual_path
                else:
                    print("❌ Invalid path. Exiting.")
                    sys.exit(1)
        
        try:
            print(f"🔄 Connecting to ChromaDB at: {chroma_db_path}")
            self.client = chromadb.PersistentClient(path=chroma_db_path)
            self.collection = self.client.get_collection("youtube_videos")
            count = self.collection.count()
            print(f"✅ Connected to ChromaDB with {count} videos")
        except Exception as e:
            print(f"❌ Error connecting to ChromaDB: {e}")
            print(f"💡 Make sure:")
            print(f"   1. The path '{chroma_db_path}' is correct")
            print(f"   2. You've run the vector DB setup script")
            print(f"   3. The collection 'youtube_videos' exists")
            sys.exit(1)
        
    def get_video_transcript(self, video_id: str) -> Optional[Tuple[str, dict]]:
        """Fetch transcript from ChromaDB using video ID"""
        try:
            print(f"🔍 Searching for video ID: {video_id}")
            results = self.collection.get(ids=[video_id])
            
            if not results['metadatas']:
                print(f"❌ Video ID '{video_id}' not found in database")
                return None
            
            metadata = results['metadatas'][0]
            
            # Try to get full transcript first, then fallback to preview
            transcript = metadata.get('transcript', '') 
            if not transcript or transcript in ['None', 'nan', '']:
                transcript = metadata.get('transcript_preview', '')
            
            if not transcript or transcript in ['None', 'nan', '']:
                print(f"❌ No transcript available for video '{video_id}'")
                return None
                
            print(f"✅ Found transcript: {len(transcript)} characters")
            return transcript, metadata
            
        except Exception as e:
            print(f"❌ Error fetching transcript: {e}")
            return None

    def check_ollama_models(self) -> list:
        """Check available Ollama models"""
        try:
            print("🔍 Checking Ollama connection...")
            response = requests.get('http://localhost:11434/api/tags', timeout=10)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [model['name'] for model in models]
                print(f"✅ Found {len(model_names)} models")
                return model_names
            else:
                print(f"❌ Ollama API returned status: {response.status_code}")
                return []
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to Ollama. Make sure it's running on localhost:11434")
            return []
        except Exception as e:
            print(f"❌ Error checking models: {e}")
            return []

    def summarize_with_ollama(self, transcript: str, video_title: str, model: str = "llama2") -> Optional[str]:
        """Summarize transcript using local Ollama LLM"""
        try:
            # Truncate transcript if too long
            max_length = 8000  # Increased for better context
            if len(transcript) > max_length:
                print(f"⚠️  Transcript too long ({len(transcript)} chars), truncating to {max_length} chars")
                transcript = transcript[:max_length]
            
            prompt = f"""
            Please provide a comprehensive and well-structured summary of the following YouTube video.

            VIDEO TITLE: {video_title}

            TRANSCRIPT:
            {transcript}

            Please organize your summary in the following format:

            ## 📌 MAIN TOPIC
            [Briefly state the main subject of the video]

            ## 🔑 KEY POINTS
            [List 5-7 most important points covered, using bullet points]

            ## 🎯 KEY FINDINGS/DISCOVERIES
            [Highlight any significant discoveries, facts, or revelations]

            ## 💡 TAKEAWAYS
            [Summarize the main lessons or conclusions]

            Keep the summary informative but concise. Focus on the most important information.
            Use clear, engaging language.
            """
            
            print(f"🤖 Generating summary using {model}...")
            print("⏳ This may take a few minutes depending on transcript length...")
            start_time = time.time()
            
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': model,
                    'prompt': prompt,
                    'stream': False,
                    'options': {
                        'temperature': 0.3,
                        'top_p': 0.9,
                        'num_ctx': 8192  # Larger context window
                    }
                },
                timeout=300  # 5 minute timeout
            )
            
            if response.status_code == 200:
                elapsed_time = time.time() - start_time
                print(f"✅ Summary generated in {elapsed_time:.1f} seconds")
                return response.json()['response']
            else:
                print(f"❌ Ollama API error: {response.status_code}")
                return None
                
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to Ollama. Make sure Ollama is running:")
            print("  1. Install Ollama from https://ollama.ai")
            print("  2. Run: ollama serve")
            print("  3. Pull a model: ollama pull llama2")
            return None
        except requests.exceptions.Timeout:
            print("❌ Request timeout. The model might be taking too long to respond.")
            return None
        except Exception as e:
            print(f"❌ Error with Ollama: {e}")
            return None

def check_ollama_running():
    """Check if Ollama is running"""
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    print("🎥 VIDEO SUMMARIZATION TOOL (Ollama + GPU)")
    print("=" * 60)
    
    # Check if Ollama is running
    if not check_ollama_running():
        print("❌ Ollama is not running. Please start it first:")
        print("  1. Open a new terminal")
        print("  2. Run: ollama serve")
        print("  3. Wait for it to start, then run this script again")
        return
    
    # Create summarizer with auto path detection
    summarizer = VideoSummarizer()
    
    # Check available models
    available_models = summarizer.check_ollama_models()
    
    if not available_models:
        print("\n💡 No models found. Please install a model:")
        print("   ollama pull llama2")
        print("   ollama pull mistral")
        return
    
    print("\n✅ Available models:")
    for i, model in enumerate(available_models, 1):
        print(f"   {i}. {model}")
    
    # Get video ID
    video_id = input("\n🎯 Enter Video ID: ").strip()
    if not video_id:
        print("❌ Please enter a valid Video ID")
        return
    
    # Show some example video IDs from your dataset
    print("\n💡 Example Video IDs from your dataset:")
    print("   t8txtQkhMcY - Scientists Can't Explain Mountain in Tibet")
    print("   mmIidOoHCfs - $138 Million Pirate Treasure")
    print("   QBHjeGGtIKE - Rubber Band Door Safety")
    
    # Model selection
    print(f"\n🤖 Select model (default: {available_models[0]}):")
    model_choice = input("Enter choice number or model name: ").strip()
    
    if model_choice.isdigit() and 1 <= int(model_choice) <= len(available_models):
        selected_model = available_models[int(model_choice) - 1]
    elif model_choice in available_models:
        selected_model = model_choice
    else:
        selected_model = available_models[0]
    
    print(f"🤖 Using model: {selected_model}")
    
    # Get transcript and generate summary
    result = summarizer.get_video_transcript(video_id)
    if not result:
        print(f"\n💡 Try these Video IDs:")
        print("   t8txtQkhMcY, mmIidOoHCfs, QBHjeGGtIKE")
        return
    
    transcript, metadata = result
    video_title = metadata.get('title', 'Unknown Title')
    channel_name = metadata.get('channel_title', 'Unknown Channel')
    views = metadata.get('view_count', 0)
    
    print(f"\n📺 Video: {video_title}")
    print(f"🏢 Channel: {channel_name}")
    print(f"👀 Views: {views:,}")
    
    summary = summarizer.summarize_with_ollama(transcript, video_title, selected_model)
    
    if summary:
        print("\n" + "=" * 80)
        print("📋 VIDEO SUMMARY")
        print("=" * 80)
        print(summary)
        print("=" * 80)
        
        # Save to file
        save_choice = input("\n💾 Save summary to file? (y/n): ").strip().lower()
        if save_choice == 'y':
            filename = f"summary_{video_id}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Video Summary\n")
                f.write(f"{'='*50}\n")
                f.write(f"Video ID: {video_id}\n")
                f.write(f"Title: {video_title}\n")
                f.write(f"Channel: {channel_name}\n")
                f.write(f"Views: {views:,}\n")
                f.write(f"Model: {selected_model}\n")
                f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"\nSummary:\n{summary}\n")
            print(f"✅ Summary saved to {filename}")
    
    else:
        print("❌ Failed to generate summary")

if __name__ == "__main__":
    main()