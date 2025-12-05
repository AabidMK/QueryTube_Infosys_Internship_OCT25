import pandas as pd
import requests
import time
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
from youtube_transcript_api.formatters import TextFormatter
# Make sure you have this installed: pip install fake-useragent
from fake_useragent import UserAgent

# --- Proxy Configuration (REQUIRED IF IP IS STILL BLOCKED) ---
# If you are using a VPN, keep this as None.
# If using a proxy, replace None with 'http://username:password@proxy_ip:port'
PROXY_URL = None

# --- Custom API Client to Handle IP Blocks ---
class CustomTranscriptsApi(YouTubeTranscriptApi):
    """Overrides the default API to use rotating User-Agents and optional Proxies."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = requests.Session()

    def _get_html(self, url, headers=None, attempt=0):
        ua = UserAgent(fallback='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36')
        current_headers = headers.copy() if headers else {}
        current_headers['User-Agent'] = ua.random
        proxies = {'http': PROXY_URL, 'https': PROXY_URL} if PROXY_URL else None
        return self.session.get(url, timeout=20, headers=current_headers, proxies=proxies).text

# --- Configuration ---
INPUT_CSV_PATH = "dataschool_dataset.csv"
OUTPUT_CSV_PATH = "dataschool_transcripts_video_metadata.csv" # Changed output filename
VIDEO_ID_COLUMN = 'video_id'
MAX_RETRIES = 5  # Adjusted retries
RETRY_DELAY = 10 # Adjusted wait time

# --- Step 1 & 2: Load Data and Initialize API ---
try:
    df = pd.read_csv(INPUT_CSV_PATH)
except FileNotFoundError:
    print(f"❌ Error: Input file not found at '{INPUT_CSV_PATH}'.")
    exit()

video_ids_to_process = df[VIDEO_ID_COLUMN].dropna().unique().tolist()
print(f"🎬 Successfully loaded dataset from: {INPUT_CSV_PATH}")
print(f"🎬 Found {len(video_ids_to_process)} unique videos to process")

ytt_api = CustomTranscriptsApi()
formatter = TextFormatter()
# Stores tuples: (video_id, transcript_text_or_error_code, is_available_boolean)
transcript_results = []

# --- Step 3: Fetch transcripts with Retries ---
for i, vid in enumerate(video_ids_to_process, start=1):
    if not isinstance(vid, str) or len(vid) != 11:
        print(f"❌ [{i}/{len(video_ids_to_process)}] Skipping invalid Video ID: {vid}")
        transcript_results.append((vid, "Invalid_ID", False))
        continue

    transcript_text = None
    is_available = False
    status_message = ""
    attempt = 0

    while attempt < MAX_RETRIES:
        try:
            transcript_list = ytt_api.list(vid)
            search_langs = ['en', 'es', 'fr', 'de']
            transcript = None
            try:
                transcript = transcript_list.find_manually_created_transcript(search_langs)
            except:
                transcript = transcript_list.find_generated_transcript(['en'])

            transcript_data = transcript.fetch()
            transcript_text = formatter.format_transcript(transcript_data)
            is_available = True # Mark as available only on successful fetch
            status_message = f"✅ [{i}/{len(video_ids_to_process)}] Transcript fetched for {vid}"
            print(status_message)
            break # Success

        except TranscriptsDisabled:
            status_message = f"⚠️ [{i}/{len(video_ids_to_process)}] Transcripts disabled for {vid}"
            transcript_text = "Transcripts_Disabled"
            is_available = False
            print(status_message)
            break

        except NoTranscriptFound:
            status_message = f"⚠️ [{i}/{len(video_ids_to_process)}] No suitable transcript found for {vid}"
            transcript_text = "No_Transcript_Found"
            is_available = False
            print(status_message)
            break

        except VideoUnavailable:
            status_message = f"❌ [{i}/{len(video_ids_to_process)}] Video unavailable: {vid}"
            transcript_text = "Video_Unavailable"
            is_available = False
            print(status_message)
            break

        except Exception as e:
            error_name = e.__class__.__name__
            if 'IpBlocked' in str(e) or 'RequestBlocked' in str(e) or error_name in ['RequestBlocked', 'ConnectionError', 'ReadTimeout']:
                attempt += 1
                if attempt < MAX_RETRIES:
                    print(f"❌ [{i}/{len(video_ids_to_process)}] **BLOCKED/Timeout**. Retrying in {RETRY_DELAY}s (Attempt {attempt}/{MAX_RETRIES})...")
                    time.sleep(RETRY_DELAY)
                    continue
                else:
                    status_message = f"❌ [{i}/{len(video_ids_to_process)}] Final failure for {vid}: Max Retries Reached."
                    transcript_text = "Error: IpBlocked"
                    is_available = False
                    print(status_message)
                    break
            else:
                status_message = f"❌ [{i}/{len(video_ids_to_process)}] Unexpected error fetching for {vid}: {error_name}"
                transcript_text = f"Error: {error_name}"
                is_available = False
                print(status_message)
                break

    transcript_results.append((vid, transcript_text, is_available))
    time.sleep(1.5) # Slightly increased base delay

# --- Step 4: Merge results back into the original DataFrame ---

# Create a temporary DataFrame from the fetched results
transcripts_df = pd.DataFrame(transcript_results, columns=[VIDEO_ID_COLUMN, 'transcript', 'is_transcript_available'])

# Merge the new transcript and availability status back into the original DataFrame (df)
# Use 'left' merge to keep all original rows from df
df = pd.merge(df, transcripts_df, on=VIDEO_ID_COLUMN, how='left')

# --- Step 5: Save the final DataFrame ---
# Ensure the columns are in a reasonable order if needed, placing new ones at the end
# Example: Move 'is_transcript_available' and 'transcript' to the end
original_cols = [col for col in df.columns if col not in ['transcript', 'is_transcript_available']]
final_cols = original_cols + ['is_transcript_available', 'transcript']
df = df[final_cols]


df.to_csv(OUTPUT_CSV_PATH, index=False, encoding='utf-8')

# --- Step 6: Summary ---
# Count based on the boolean column
success_count = df['is_transcript_available'].sum()
total_processed = len(video_ids_to_process)
errors_and_missing = total_processed - success_count

print("\n━━━━━ Summary ━━━━━")
print(f"✅ Transcripts successfully fetched: {int(success_count)}") # Cast to int for clean output
print(f"⚠️ Missing/Errors (Processed Videos): {errors_and_missing}")
print(f"📊 Total unique videos processed: {total_processed}")
print(f"💾 Saved final dataset (with all columns) to: {OUTPUT_CSV_PATH}")
print("━━━━━━━━━━━━━━━━━━━━")