import google.generativeai as genai
import pickle
import os
from dotenv import load_dotenv
load_dotenv()
api_key=os.getenv("API_KEY")
genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.0-flash")


video_id = input("Enter video_ID : ").strip()

with open("final_metadata.pkl", "rb") as f:
    metadata = pickle.load(f)

video_data = next((item for item in metadata if item["id"] == video_id), None)
transcript = video_data["transcript"] if video_data else None

# Generate summary
if transcript and transcript.strip():
    prompt = f"Summarize this YouTube video transcript in 5 lines:\n\n{transcript}"
    response = model.generate_content(prompt)
    print("\nVideo Summary:\n", response.text)
else:
    print("Transcript not found or empty for this video ID.")
