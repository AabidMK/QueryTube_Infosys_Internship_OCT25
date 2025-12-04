import pandas as pd
import chromadb
from chromadb.config import Settings
import google.generativeai as genai
import time
import os
from config import YOUR_GEMINI_KEY

# ================================================
# 1. Configure Gemini API
# ================================================
genai.configure(api_key=YOUR_GEMINI_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# ================================================
# 2. Load CSV Dataset
# ================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "masterdataset_with_embeddings.csv")

df = pd.read_csv(CSV_PATH, on_bad_lines="skip", encoding="utf-8")
print("✅ Dataset loaded successfully!")
print("Rows:", len(df))

# Required columns
required_cols = ["id", "transcript", "embedding", "title",
                 "channel_title", "viewCount", "duration"]

for col in required_cols:
    if col not in df.columns:
        raise ValueError(f"Missing required column: {col}")

# Fix empty IDs
df["id"] = df["id"].fillna("").astype(str)
df.loc[df["id"].str.strip() == "", "id"] = [
    f"auto_id_{i}" for i in range(len(df[df["id"].str.strip() == ""]))
]

# Convert embedding string → list of floats
def parse_embedding(x):
    if isinstance(x, str):
        x = x.strip("[]")
        try:
            return [float(i) for i in x.split(",") if i.strip()]
        except:
            return []
    return x

df["embedding"] = df["embedding"].apply(parse_embedding)

# ================================================
# 3. Initialize ChromaDB
# ================================================
client = chromadb.Client(Settings(anonymized_telemetry=False, is_persistent=False))

collection = client.create_collection(
    name="youtube_embeddings_final_fast",
    get_or_create=True
)

collection.add(
    ids=df["id"].tolist(),
    embeddings=df["embedding"].tolist(),
    metadatas=[
        {
            "title": row["title"],
            "transcript": row["transcript"],
            "channel_title": row["channel_title"],
            "viewCount": row["viewCount"],
            "duration": row["duration"],
        }
        for _, row in df.iterrows()
    ],
)

print("✅ All data inserted into ChromaDB!")


# ================================================
# 4. Clean Bullet-Point Summarization
# ================================================
def summarize_with_gemini(transcript, title):
    prompt = f"""
    You are an expert YouTube summarizer.

    Summarize the video titled: **{title}**

    Return **5–6 bullet points**, short, clear, clean.
    Rules:
    - No paragraphs
    - No '*' symbols
    - Format like:
        1. point
        2. point
        3. point
    - Each bullet must be one concise idea.

    Transcript:
    {transcript}
    """

    for attempt in range(3):
        try:
            response = model.generate_content(prompt)
            text = response.text.strip()

            bullets = []

            # Extract bullets: lines beginning with "1.", "2.", etc.
            for line in text.split("\n"):
                line = line.strip()
                if line and (line[0].isdigit() and "." in line[:3]):
                    cleaned = line[line.find(".") + 1:].strip()
                    bullets.append(cleaned)

            # Ensure 5–6 bullets minimum
            if len(bullets) < 5:
                return bullets

            return bullets

        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                print("⏳ Rate limit hit. Retrying...")
                time.sleep(2)
                continue
            return [f"Error generating summary: {e}"]

    return ["Summarization failed after retries."]


# ================================================
# 5. FastAPI Callable Function
# ================================================
def summarize_video(video_id: str):
    """
    Returns:
    {
        "video_id": "...",
        "title": "...",
        "channel": "...",
        "summary_points": [...]
    }
    """
    result = collection.get(ids=[video_id])

    if not result or len(result["ids"]) == 0:
        return None

    metadata = result["metadatas"][0]

    transcript = metadata.get("transcript", "")
    title = metadata.get("title", "Untitled Video")
    channel = metadata.get("channel_title", "Unknown Channel")

    # Ask Gemini to summarize
    summary_points = summarize_with_gemini(transcript, title)

    return {
        "video_id": video_id,
        "title": title,
        "channel": channel,
        "summary_points": summary_points
    }
