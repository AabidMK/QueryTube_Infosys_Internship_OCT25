import os
import chromadb
from google import genai
from google.genai.errors import APIError


%env GEMINI_API_KEY=AIzaSyBJvh2HjCThwscdBxHk33NDDiKESZLIUus




VECTOR_DB_PATH = './chroma_db'
COLLECTION_NAME = 'video_analysis_collection'
MODEL_NAME = 'gemini-2.5-flash' # Fast and efficient for summarization


def get_transcript_from_db(video_id: str) -> str | None:
    """
    Connects to ChromaDB and retrieves the transcript for a given video ID.
    """
    print(f"--- 1. Connecting to ChromaDB and Fetching Transcript for ID: {video_id} ---")
    try:
      
        client = chromadb.PersistentClient(path=VECTOR_DB_PATH)
        collection = client.get_collection(name=COLLECTION_NAME)
        
        
        results = collection.get(
            ids=[video_id],
            include=['documents']
        )
        
        if results['ids']:
           
            transcript = results['documents'][0]
            print(f"✅ Transcript retrieved successfully! Length: {len(transcript)} characters.")
            return transcript
        else:
            print(f"❌ Video ID '{video_id}' not found in the collection.")
            return None
            
    except Exception as e:
        print(f"❌ Error during database retrieval: {e}")
        return None

def summarize_transcript_with_gemini(transcript: str, video_title: str) -> str | None:
    """
    Sends the transcript to the Gemini API for summarization.
    """
    print("\n--- 2. Sending Transcript to Gemini for Summarization ---")
    
  
    if 'GEMINI_API_KEY' not in os.environ:
         
        print("❌ ERROR: GEMINI_API_KEY environment variable not set. Please check the %env command.")
        return None
    
    try:
       )
        client = genai.Client()

       
        prompt = f"""
        Please provide a concise, engaging summary of the following video transcript. 
        The video title is: "{video_title}".
        
        Focus on the main topics, key facts, and conclusions. The summary should be easy to read and no longer than 3-4 paragraphs.
        
        TRANSCRIPT:
        ---
        {transcript}
        ---
        """
        

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )
        
        print("✅ Summarization complete.")
        return response.text
        
    except APIError as e:
        print(f"❌ Gemini API Error: {e}")
        return None
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        return None



if __name__ == "__main__":
    
    
    VIDEO_ID_TO_SUMMARIZE = 't8txtqkhmcy'
    VIDEO_TITLE = 'scientists cant explain whats happening on this mountain in tibet' # Title used for better context in the prompt

  
    full_transcript = get_transcript_from_db(VIDEO_ID_TO_SUMMARIZE)
    
    if full_transcript:
      
        summary = summarize_transcript_with_gemini(full_transcript, VIDEO_TITLE)
        
       
        if summary:
            print("\n" + "="*50)
            print(f"✨ FINAL SUMMARY for Video ID: {VIDEO_ID_TO_SUMMARIZE}")
            print(f"Title: {VIDEO_TITLE}")
            print("="*50)
            print(summary)
            print("="*50)