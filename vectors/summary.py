import os
import pickle
import pandas as pd
from dotenv import load_dotenv
import google.generativeai as genai
from typing import Optional, Dict, Any

# Load environment variables
load_dotenv()

class SimpleVideoSummarizer:
    def __init__(self, pickle_file: str = "metadata_mapping.pkl", csv_file: str = "final_embeddings.csv"):
        """Initialize with correct transcript column"""
        self.pickle_file = pickle_file
        self.csv_file = csv_file
        self.metadata_mapping = {}
        self.video_details = {}
        self.transcripts_data = {}
        
        try:
            # Load data
            self._load_metadata_mapping()
            self._load_transcripts_data()
            
            # Initialize Gemini API
            self._setup_gemini()
            
            print("✅ Video Summarizer initialized successfully")
            
        except Exception as e:
            print(f"❌ Error initializing: {e}")
            raise
    
    def _load_metadata_mapping(self):
        """Load metadata mapping from pickle file"""
        with open(self.pickle_file, 'rb') as f:
            self.metadata_mapping = pickle.load(f)
        
        # Extract video details
        self.video_details = {}
        video_details_list = self.metadata_mapping.get('video_details', [])
        
        for video in video_details_list:
            video_id = video.get('original_id')
            if video_id:
                self.video_details[video_id] = {
                    'title': video.get('title', 'Unknown Title'),
                    'channel_title': video.get('channel', 'Unknown Channel'),
                    'view_count': video.get('view_count', 0),
                    'duration': video.get('duration', ''),
                    'description': video.get('description', '')
                }
    
    def _load_transcripts_data(self):
        """Load transcripts from CSV file with correct column"""
        df = pd.read_csv(self.csv_file)
        
        # Use the actual 'transcript' column
        transcript_column = 'transcript'
        
        if transcript_column in df.columns:
            for _, row in df.iterrows():
                video_id = row.get('id')
                if video_id and pd.notna(video_id):
                    transcript = row.get(transcript_column, '')
                    if pd.notna(transcript) and transcript and transcript != 'False':
                        self.transcripts_data[str(video_id)] = str(transcript)
    
    def _setup_gemini(self):
        """Setup Google Gemini API with correct model"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("❌ GEMINI_API_KEY not found in .env file")
        
        genai.configure(api_key=api_key)
        
        # List available models to see what's accessible
        try:
            models = genai.list_models()
            print("🔍 Available Gemini models:")
            for model in models:
                if 'generateContent' in model.supported_generation_methods:
                    print(f"   ✅ {model.name}")
            
            # Try different model names
            model_names = ['gemini-flash-latest']
            self.model = None
            
            for model_name in model_names:
                try:
                    self.model = genai.GenerativeModel(model_name)
                    print(f"✅ Using model: {model_name}")
                    break
                except Exception:
                    continue
            
            if self.model is None:
                # Fallback to the first available model that supports generateContent
                for model in models:
                    if 'generateContent' in model.supported_generation_methods:
                        self.model = genai.GenerativeModel(model.name)
                        print(f"✅ Using fallback model: {model.name}")
                        break
            
            if self.model is None:
                raise ValueError("No suitable Gemini model found")
                
        except Exception as e:
            print(f"❌ Error setting up Gemini: {e}")
            raise
    
    def get_video_data(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get complete video data by video_id"""
        video_id = str(video_id).strip()
        
        # Look in video details
        video_metadata = self.video_details.get(video_id)
        
        if not video_metadata:
            return None
        
        # Get transcript
        transcript = self.transcripts_data.get(video_id, '')
        
        return {
            'video_id': video_id,
            'title': video_metadata['title'],
            'channel_title': video_metadata['channel_title'],
            'view_count': video_metadata['view_count'],
            'duration': video_metadata['duration'],
            'description': video_metadata['description'],
            'transcript': transcript
        }
    
    def summarize_video(self, video_id: str) -> Dict[str, Any]:
        """Main function to summarize a video"""
        print(f"🎬 Processing: {video_id}")
        
        # Get video data
        video_data = self.get_video_data(video_id)
        if not video_data:
            return {"error": f"Video '{video_id}' not found"}
        
        # Check transcript
        transcript = video_data['transcript']
        if len(transcript.strip()) < 100:
            return {
                "error": f"Transcript too short ({len(transcript)} chars)",
                "video_id": video_id,
                "title": video_data['title']
            }
        
        # Generate summary
        print("🤖 Generating summary...")
        summary = self._generate_summary(transcript, video_data['title'], video_data['description'])
        
        if not summary:
            return {
                "error": "Failed to generate summary",
                "video_id": video_id,
                "title": video_data['title']
            }
        
        # Return complete result
        return {
            "video_id": video_id,
            "title": video_data['title'],
            "channel_title": video_data['channel_title'],
            "view_count": video_data['view_count'],
            "duration": video_data['duration'],
            "summary": summary,
            "transcript_length": len(transcript)
        }
    
    def _generate_summary(self, transcript: str, title: str, description: str = "") -> str:
        """Generate summary using Gemini"""
        try:
            context = f"Title: {title}"
            if description:
                context += f"\nDescription: {description}"
            
            prompt = f"""
            Please provide a comprehensive summary of the following video content.
            
            {context}
            
            Transcript:
            {transcript[:12000]}
            
            Please provide a well-structured summary with:
            
            ## Main Topic
            What is this video primarily about?
            
            ## Key Points  
            3-5 main points covered
            
            ## Key Takeaways
            Important insights or conclusions
            
            ## Overall Summary
            Brief 2-3 sentence overview
            """
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            print(f"❌ Summarization error: {e}")
            return None
    
    def display_summary(self, result: Dict[str, Any]):
        """Display the summary"""
        if "error" in result:
            print(f"\n❌ Error: {result['error']}")
            return
        
        print(f"\n" + "="*80)
        print("🎬 VIDEO SUMMARY")
        print("="*80)
        print(f"📺 Title: {result['title']}")
        print(f"👨‍💼 Channel: {result['channel_title']}")
        print(f"🆔 Video ID: {result['video_id']}")
        print(f"👀 Views: {result['view_count']}")
        print(f"⏱️ Duration: {result['duration']}")
        print(f"📝 Transcript Length: {result['transcript_length']} characters")
        print("\n" + "="*80)
        print("📋 SUMMARY")
        print("="*80)
        print(result['summary'])
        print("="*80)

def main():
    """Main function - simple video ID input only"""
    print("🚀 Video Summarizer")
    
    try:
        summarizer = SimpleVideoSummarizer()
        
        while True:
            video_id = input("\n🔍 Enter Video ID (or 'quit' to exit): ").strip()
            
            if video_id.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not video_id:
                print("❌ Please enter a Video ID")
                continue
            
            # Get and display summary
            result = summarizer.summarize_video(video_id)
            summarizer.display_summary(result)
                
    except Exception as e:
        print(f"❌ Failed to start: {e}")

if __name__ == "__main__":
    main()