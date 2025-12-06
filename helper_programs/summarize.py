# summarize.py
import chromadb
from groq import Groq
from dotenv import load_dotenv
import os

# ------------------------------
# Load environment variables
# ------------------------------
load_dotenv()  # ✅ Load .env file

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("❌ GROQ_API_KEY is missing! Add it to your .env file.")

client_groq = Groq(api_key=GROQ_API_KEY)

# Initialize Chroma client
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# ------------------------------
# Fetch transcript by video_id
# ------------------------------
def get_transcript_from_db(video_id, collection_name="youtube_videos"):
    try:
        collection = chroma_client.get_collection(collection_name)
        result = collection.get(ids=[video_id])

        if not result["documents"] or len(result["documents"]) == 0:
            return None
        
        return result["documents"][0]
    except Exception as e:
        print(f"Error getting transcript: {e}")
        return None

# ------------------------------
# Summarize using Groq Mixtral
# ------------------------------
def summarize_text(transcript, max_tokens=350):
    if not transcript:
        return "No transcript available for summarization."

    prompt = f"""
    Summarize the following YouTube transcript into clear, concise bullet points.
    Avoid filler words, maintain meaning, and keep it easy to read.

    Transcript:
    {transcript}

    Summary:
    """

    try:
        response = client_groq.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.4
        )

        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error during summarization: {e}")
        return "Error generating summary. Please try again later."

# ------------------------------
# Main Execution (only runs when script is run directly)
# ------------------------------
if __name__ == "__main__":
    video_id = input("🎬 Enter Video ID to summarize: ").strip()

    transcript = get_transcript_from_db(video_id)

    if not transcript:
        print("❌ Transcript not found in Vector DB. Make sure embeddings & transcripts are stored first.")
        exit()

    print("\n📝 Generating summary... Please wait...\n")
    summary = summarize_text(transcript)

    print("✅ Summary Ready!\n")
    print(summary)