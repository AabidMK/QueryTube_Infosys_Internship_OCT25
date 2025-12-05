# ============================================
# ✅ IMPORTS
# ============================================
import os
import textwrap
import google.generativeai as genai
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, PayloadSchemaType

# ============================================
# ✅ QDRANT CONFIG
# ============================================
qdrant_client = QdrantClient(
    url="https://63f7ff1e-6ee2-4835-947c-10c1a734cb1e.eu-central-1-0.aws.cloud.qdrant.io",
    api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.-jeQEhiuo5KV5Q3Ha-YfUatW13_iR3olPapJNQqIgwk"
)

# IMPORTANT — change to your 622-video collection
collection_name = "youtube_videos_full_payload"

# Ensure index creation for the correct field: `id`
try:
    qdrant_client.create_payload_index(
        collection_name=collection_name,
        field_name="id",                 # FIXED
        field_schema=PayloadSchemaType.KEYWORD
    )
    print("✅ Index created for 'id'")
except Exception:
    print("ℹ️ Index already exists — skipping")


# ============================================
# ✅ GEMINI API CONFIG
# ============================================
os.environ["GEMINI_API_KEY"] = "AIzaSyCEL0u89YrxXgF1k1dWnj6Ye_Jcfvvzj88"
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")


# ============================================
# ✅ FUNCTION: FETCH TRANSCRIPT FROM QDRANT
# ============================================
def fetch_from_qdrant(video_id: str):
    """
    Retrieves title + transcript using 'id' field (correct for your dataset).
    """

    result = qdrant_client.query_points(
        collection_name=collection_name,
        limit=1,
        with_payload=True,
        query_filter=Filter(
            must=[
                FieldCondition(
                    key="id",                  # FIXED (your dataset uses 'id')
                    match=MatchValue(value=video_id)
                )
            ]
        )
    )

    if not result.points:
        return None, None

    payload = result.points[0].payload
    title = payload.get("title", "Untitled Video")
    transcript = payload.get("transcript", "")  # FIXED

    return title, transcript


# ============================================
# ✅ FUNCTION: SUMMARIZE TRANSCRIPT WITH GEMINI
# ============================================
def summarize_transcript(transcript: str, title: str):

    if not transcript or not transcript.strip():
        return "⚠️ No transcript available for this video."

    CHUNK_SIZE = 7000  # Safe chunk for Gemini
    chunks = textwrap.wrap(transcript, CHUNK_SIZE)

    partial_summaries = []

    for i, chunk in enumerate(chunks):
        prompt = f"""
        Summarize this YouTube transcript clearly and concisely.

        Video Title: {title}
        Chunk {i+1}/{len(chunks)}:

        {chunk}
        """

        try:
            response = model.generate_content(prompt)
            partial_summaries.append(response.text.strip())
        except Exception as e:
            partial_summaries.append(f"[Error in chunk {i+1}: {e}]")

    # Merge partial summaries
    merge_prompt = f"""
    Combine the following partial summaries into one final,
    well-structured summary for the video: "{title}".

    Partial Summaries:
    {partial_summaries}
    """

    final_response = model.generate_content(merge_prompt)
    return final_response.text.strip()


# ============================================
# ✅ MAIN EXECUTION
# ============================================
video_id = input("🎥 Enter YouTube video ID: ").strip()

title, transcript = fetch_from_qdrant(video_id)

if title is None:
    print("⚠️ No video found in Qdrant for this ID.")
else:
    print(f"\n🧠 Generating summary for: {title}...\n")
    summary = summarize_transcript(transcript, title)
    print("📝 Summary:\n")
    print(summary)
