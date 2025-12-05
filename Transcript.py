import os
import time
import pandas as pd
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
from youtube_transcript_api.formatters import TextFormatter

# ---------------- CONFIG ---------------- #
CSV_FILE = "channel_videos_full.csv"
SAVE_INTERVAL = 10  # Save progress every N videos
# ----------------------------------------- #

def get_transcript(video_id):
    """
    Fetches English transcript if available.
    Handles errors and logs the cause if unable.
    Returns transcript text and a boolean indicating availability.
    """
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.list(video_id)

        transcript = None
        try:
            # Try to get manually created transcript first
            transcript = transcript_list.find_manually_created_transcript(['en'])
        except:
            try:
                # Fall back to auto-generated transcript
                transcript = transcript_list.find_generated_transcript(['en'])
            except:
                return "No English transcript found.", False

        if transcript:
            transcript_data = transcript.fetch()
            formatter = TextFormatter()
            text = formatter.format_transcript(transcript_data.snippets)
            return text, True
        else:
            return "No English transcript found.", False

    except TranscriptsDisabled:
        return "Transcripts are disabled for this video.", False
    except NoTranscriptFound:
        return "No English transcript found.", False
    except VideoUnavailable:
        return "Video is unavailable.", False
    except Exception as e:
        return f"Error: {str(e)}", False

def main():
    # Load existing CSV
    if not os.path.exists(CSV_FILE):
        print(f"Error: {CSV_FILE} not found!")
        return

    print(f"Loading video data from {CSV_FILE}...")
    df = pd.read_csv(CSV_FILE)
    print(f"Loaded {len(df)} videos")

    # Count existing transcripts
    existing_count = df['is_transcript_available'].sum() if 'is_transcript_available' in df.columns else 0
    print(f"Already have {existing_count} transcripts")

    print("Fetching transcripts (English)...")
    processed_count = 0
    success_count = 0

    try:
        for idx, row in df.iterrows():
            video_id = row["id"]

            # Skip if transcript already exists
            if pd.notna(row.get("transcript")) and row.get("is_transcript_available") == True:
                print(f"[{idx+1}/{len(df)}] Skipping {row['title'][:50]}... - already exists")
                continue

            transcript_text, available = get_transcript(video_id)
            df.at[idx, "transcript"] = transcript_text
            df.at[idx, "is_transcript_available"] = available

            processed_count += 1
            if available:
                success_count += 1
                print(f"[{idx+1}/{len(df)}] SUCCESS: Fetched: {row['title'][:50]}...")
            else:
                print(f"[{idx+1}/{len(df)}] FAILED: Not available: {row['title'][:50]}... - {transcript_text}")

            # Save periodically
            if processed_count % SAVE_INTERVAL == 0:
                df.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")
                print(f"Progress saved ({processed_count} processed, {success_count} successful)")

            time.sleep(1)  # To avoid API rate limits

    except KeyboardInterrupt:
        print("\nInterrupted by user. Saving progress...")

    print("Saving final results to CSV...")
    df.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")
    print(f"Data saved to {CSV_FILE}")

    total_with_transcripts = df['is_transcript_available'].sum()
    print(f"\nFinal Summary:")
    print(f"   Total videos: {len(df)}")
    print(f"   With transcripts: {total_with_transcripts}")
    print(f"   Without transcripts: {len(df) - total_with_transcripts}")
    print(f"   Newly processed: {processed_count} ({success_count} successful)")

if __name__ == "__main__":
    main()

