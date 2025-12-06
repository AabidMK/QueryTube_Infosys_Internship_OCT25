import streamlit as st
import pandas as pd
from youtube_transcript_api import YouTubeTranscriptApi
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
import time

# -------------------------------
# Function to fetch transcript for a single video
# -------------------------------
def fetch_transcript(video_id):
    try:
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([item['text'] for item in transcript_data])
        return {"video_id": video_id, "transcript": transcript, "status": "success"}
    except Exception as e:
        return {"video_id": video_id, "transcript": f"Error fetching transcript: {e}", "status": "failed"}

# -------------------------------
# Parallel transcript fetching with retry queue
# -------------------------------
def fetch_all_transcripts_parallel(video_ids, max_workers=5, max_retries=100):
    results = []
    retry_queue = Queue()

    def process_batch(ids):
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(fetch_transcript, vid): vid for vid in ids}
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                if result["status"] == "failed":
                    retry_queue.put(result["video_id"])
                st.write(f"✅ Processed: {result['video_id']} ({result['status']})")

    # 1️⃣ First batch
    st.info("🚀 Starting parallel transcript fetching...")
    process_batch(video_ids)

    # 2️⃣ Retry failed items
    for attempt in range(1, max_retries + 1):
        if retry_queue.empty():
            break
        st.warning(f"🔁 Retry attempt {attempt}/{max_retries} for failed videos...")
        retry_ids = []
        while not retry_queue.empty():
            retry_ids.append(retry_queue.get())

        time.sleep(2)
        process_batch(retry_ids)

    # Create DataFrame and return only successful ones
    df = pd.DataFrame(results)
    successful_df = df[df["status"] == "success"][["video_id", "transcript"]]
    return successful_df

# -------------------------------
# Streamlit UI
# -------------------------------
st.set_page_config(page_title="🎬 YouTube Transcript Downloader", page_icon="🎥")
st.title("🎬 YouTube Transcript Downloader (Parallel + Retry)")

st.write("Upload a CSV file containing YouTube video IDs (column name: `id`).")

uploaded_file = st.file_uploader("📁 Choose a CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("📊 Uploaded CSV Preview:")
    st.dataframe(df.head())

    if "id" not in df.columns:
        st.error("❌ CSV must contain a column named `id`.")
    else:
        video_ids = df["id"].dropna().tolist()

        if st.button("⚡ Fetch Transcripts in Parallel"):
            st.info("Fetching transcripts... please wait.")

            df_transcripts = fetch_all_transcripts_parallel(video_ids, max_workers=5)

            if df_transcripts.empty:
                st.error("❌ No transcripts were successfully fetched.")
            else:
                st.success(f"✅ Transcripts fetched successfully for {len(df_transcripts)} videos!")
                st.dataframe(df_transcripts)

                csv_download = df_transcripts.to_csv(index=False).encode("utf-8")

                st.download_button(
                    label="📥 Download Transcripts CSV (Success Only)",
                    data=csv_download,
                    file_name="youtube_transcripts_success.csv",
                    mime="text/csv"
                )
