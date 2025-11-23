import google.generativeai as genai
import pickle
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("API_KEY")
genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.0-flash")


def generate_summary_from_video(video_id):
    with open("final_metadata.pkl", "rb") as f:
        metadata = pickle.load(f)

    video_data = next((item for item in metadata if item["id"] == video_id), None)
    transcript = video_data["transcript"] if video_data else None

    if not transcript or not transcript.strip():
        return {"error": "Transcript empty or not found"}

    prompt = f"Summarize this YouTube video transcript in 5 lines:\n\n{transcript}"
    response = model.generate_content(prompt)

    return {"summary": response.text}
