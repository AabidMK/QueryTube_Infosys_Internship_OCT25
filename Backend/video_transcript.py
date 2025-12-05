import pandas as pd
import requests
import time
import random # Import the random module for randomized delays
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
from youtube_transcript_api.formatters import TextFormatter
from fake_useragent import UserAgent 

# --- Proxy Configuration (Use VPN instead, keep this None) ---
PROXY_URL = None 

# --- Custom API Client (Includes User-Agent Rotation) ---
class CustomTranscriptsApi(YouTubeTranscriptApi):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = requests.Session()

    def _get_html(self, url, headers=None, attempt=0):
        ua = UserAgent(fallback='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36')
        current_headers = headers.copy() if headers else {}
        current_headers['User-Agent'] = ua.random
        proxies = {'http': PROXY_URL, 'https': PROXY_URL} if PROX_URL else None
        return self.session.get(url, timeout=25, headers=current_headers, proxies=proxies).text # Increased timeout

# --- Configuration ---
INPUT_CSV_PATH = "dataschool_dataset.csv"
# Consider saving intermediate results if running in batches
OUTPUT_CSV_PATH = "dataschool_transcripts_output_FINAL_new.csv" 
VIDEO_ID_COLUMN = 'video_id'
MAX_RETRIES = 5  # Keep retries reasonable
RETRY_DELAY = 20 # Longer wait time for retries
BASE_DELAY = 5   # Increased base delay between successful requests
RANDOM_DELAY_MAX = 5 # Add up to 5 extra seconds randomly

# --- Optional: Batch Processing ---
# If you want to process only a subset, uncomment and set these:
# START_INDEX = 77 # Start after the last successful one
# END_INDEX = 107 # Process the next 30 (adjust as needed)

# --- Step 1 & 2: Load Data and Initialize API ---
try:
    df = pd.read_csv(INPUT_CSV_PATH)
except FileNotFoundError:
    print(f"❌ Error: Input file not found at '{INPUT_CSV_PATH}'.")
    exit()

all_video_ids = df[VIDEO_ID_COLUMN].dropna().unique().tolist()
print(f"🎬 Successfully loaded dataset from: {INPUT_CSV_PATH}")
print(f"🎬 Found {len(all_video_ids)} unique videos in total")

# Apply batch slicing if START_INDEX and END_INDEX are defined
try:
    video_ids_to_process = all_video_ids[START_INDEX:END_INDEX]
    print(f"⚙️ Processing batch: Videos {START_INDEX + 1} to {END_INDEX}")
except NameError:
    # If START_INDEX/END_INDEX are not defined, process all
    video_ids_to_process = all_video_ids
    print(f"⚙️ Processing all {len(video_ids_to_process)} videos.")


ytt_api = CustomTranscriptsApi() 
formatter = TextFormatter()
# Load existing results if the output file already exists to avoid re-fetching
try:
    df_existing = pd.read_csv(OUTPUT_CSV_PATH)
    # Convert existing transcripts to a dictionary {video_id: transcript}
    fetched_transcripts = pd.Series(df_existing['transcript'].values, index=df_existing[VIDEO_ID_COLUMN]).to_dict()
    print(f"💾 Loaded {len(fetched_transcripts)} existing results from {OUTPUT_CSV_PATH}")
except FileNotFoundError:
    fetched_transcripts = {}
    print(f"💾 No existing output file found. Starting fresh.")


# --- Step 3: Fetch transcripts with Aggressive Retries & Delays ---
new_fetches = 0
for i, vid in enumerate(video_ids_to_process, start=1):
    
    # Skip if we already have a valid result for this video ID
    if vid in fetched_transcripts and isinstance(fetched_transcripts[vid], str) and "Error" not in fetched_transcripts[vid] and "Invalid_ID" not in fetched_transcripts[vid]:
         # Optional: print(f"⏭️ [{i}/{len(video_ids_to_process)}] Skipping {vid} - Already fetched.")
        continue

    # Get the global index for accurate progress reporting
    global_index = all_video_ids.index(vid) + 1

    if not isinstance(vid, str) or len(vid) != 11:
        fetched_transcripts[vid] = "Invalid_ID"
        continue
    
    transcript_text = None
    attempt = 0
    
    while attempt < MAX_RETRIES:
        try:
            transcript_list = ytt_api.list(vid)
            
            search_langs = ['en', 'es', 'fr', 'de']
            try:
                transcript = transcript_list.find_manually_created_transcript(search_langs)
            except:
                transcript = transcript_list.find_generated_transcript(['en'])
            
            transcript_data = transcript.fetch()
            transcript_text = formatter.format_transcript(transcript_data)
            
            print(f"✅ [{global_index}/{len(all_video_ids)}] Transcript fetched for {vid}")
            new_fetches += 1
            break # Success
            
        except TranscriptsDisabled:
            print(f"⚠️ [{global_index}/{len(all_video_ids)}] Transcripts disabled for {vid}")
            transcript_text = "Transcripts_Disabled"
            break
            
        except NoTranscriptFound:
            print(f"⚠️ [{global_index}/{len(all_video_ids)}] No suitable transcript found for {vid}")
            transcript_text = "No_Transcript_Found"
            break

        except VideoUnavailable:
             print(f"❌ [{global_index}/{len(all_video_ids)}] Video unavailable: {vid}")
             transcript_text = "Video_Unavailable"
             break

        except Exception as e:
            error_name = e.__class__.__name__
            if 'IpBlocked' in str(e) or 'RequestBlocked' in str(e) or error_name in ['RequestBlocked', 'ConnectionError', 'ReadTimeout', 'TooManyRequests']:
                attempt += 1
                if attempt < MAX_RETRIES:
                    wait_time = RETRY_DELAY + random.uniform(0, RANDOM_DELAY_MAX) # Add random jitter to retry delay
                    print(f"❌ [{global_index}/{len(all_video_ids)}] **BLOCKED/Timeout**. Retrying in {wait_time:.1f}s (Attempt {attempt}/{MAX_RETRIES})...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"❌ [{global_index}/{len(all_video_ids)}] Final failure for {vid}: Max Retries Reached.")
                    transcript_text = "Error: IpBlocked"
                    break
            else:
                print(f"❌ [{global_index}/{len(all_video_ids)}] Unexpected error fetching for {vid}: {error_name}")
                transcript_text = f"Error: {error_name}"
                break
    
    fetched_transcripts[vid] = transcript_text
    
    # Apply base delay + random jitter after each video attempt
    sleep_duration = BASE_DELAY + random.uniform(0, RANDOM_DELAY_MAX)
    time.sleep(sleep_duration)

print(f"\n✨ Newly fetched transcripts in this run: {new_fetches}")

# --- Step 4 & 5: Merge (Update) and Save ---
# Create DataFrame of ALL transcripts (old and new)
all_transcripts_df = pd.DataFrame(fetched_transcripts.items(), columns=[VIDEO_ID_COLUMN, 'transcript_updated'])

# Merge this comprehensive list back into the original DataFrame
# Use 'left' join to keep all original rows, update transcript where available
df_final = pd.merge(df, all_transcripts_df, on=VIDEO_ID_COLUMN, how='left')

# Replace the original (potentially missing/old) transcript column with the updated one
# If 'transcript' column didn't exist, this adds it. If it did, it overwrites with potentially new data.
df_final['transcript'] = df_final['transcript_updated']
df_final = df_final.drop(columns=['transcript_updated']) # Clean up temporary column

df_final.to_csv(OUTPUT_CSV_PATH, index=False, encoding='utf-8')

success_count = df_final['transcript'].apply(lambda x: isinstance(x, str) and not any(err in x for err in ["Disabled", "Found", "Unavailable", "Error", "Invalid_ID"])).sum()
total_videos = len(all_video_ids)
errors_and_missing = total_videos - success_count

print("\n━━━━━ Final Summary ━━━━━")
print(f"✅ Total transcripts successfully fetched (cumulative): {success_count}")
print(f"⚠️ Total missing/errors: {errors_and_missing}")
print(f"📊 Total unique videos in dataset: {total_videos}")
print(f"💾 Saved updated dataset (with all columns) to: {OUTPUT_CSV_PATH}")
print("━━━━━━━━━━━━━━━━━━━━")