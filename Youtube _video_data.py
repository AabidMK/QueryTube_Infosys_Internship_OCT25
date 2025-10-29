pip install google-api-python-client pandas

import time
import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime
from pytz import UTC

# ========================
# CONFIGURATION
# ========================
API_KEY = "AIzaSyBAcd63DKLbbwM9ODRDY8VeoovbQFfVzAY"
CHANNEL_ID = "UC-VPf3yXgkbjH6PFKQBblYg"
YT_API_SERVICE_NAME = "youtube"
YT_API_VERSION = "v3"
CSV_FILE = "channel_videos_full.csv"

# ========================
# FUNCTION: Get channel details
# ========================
def get_channel_details(youtube, channel_id):
    """Fetch channel-level details (name, description, country, stats, etc.)"""
    request = youtube.channels().list(
        part="snippet,statistics",
        id=channel_id
    )
    response = request.execute()

    if not response.get("items"):
        return {}

    item = response["items"][0]
    snippet = item.get("snippet", {})
    stats = item.get("statistics", {})

    return {
        "channel_id": item.get("id"),
        "channel_title": snippet.get("title"),
        "channel_description": snippet.get("description"),
        "channel_country": snippet.get("country"),
        "channel_thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url"),
        "channel_subscription": stats.get("subscriberCount"),
        "channel_video_count": stats.get("videoCount"),
    }

# ========================
# FUNCTION: Fetch all videos with full details
# ========================
def get_all_videos_from_channel(api_key, channel_id, max_results_per_page=50):
    youtube = build(YT_API_SERVICE_NAME, YT_API_VERSION, developerKey=api_key)
    rows = []
    next_page_token = None
    total = 0

    # Step 1: Collect video IDs
    video_ids = []
    print("🔍 Collecting video IDs...")
    while True:
        try:
            request = youtube.search().list(
                part="id",
                channelId=channel_id,
                maxResults=max_results_per_page,
                order="date",
                type="video",
                pageToken=next_page_token
            )
            response = request.execute()

            for item in response.get("items", []):
                vid = item.get("id", {}).get("videoId")
                if vid:
                    video_ids.append(vid)

            total += len(response.get("items", []))
            print(f"Fetched {len(response['items'])} video IDs | Total so far: {total}")

            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

            time.sleep(0.1)
        except HttpError as e:
            print(f"⚠️ HttpError while collecting IDs: {e}")
            time.sleep(5)
            continue

    # Step 2: Fetch channel info once
    channel_info = get_channel_details(youtube, channel_id)

    # Step 3: Fetch video details in batches
    print("\n📥 Fetching video details...")
    for i in range(0, len(video_ids), 50):
        batch_ids = video_ids[i:i+50]
        try:
            request = youtube.videos().list(
                part="snippet,statistics,contentDetails,status",
                id=",".join(batch_ids)
            )
            response = request.execute()

            for item in response.get("items", []):
                snippet = item.get("snippet", {})
                stats = item.get("statistics", {})
                content = item.get("contentDetails", {})
                status = item.get("status", {})

                published_at = snippet.get("publishedAt")
                published_at_dt = pd.to_datetime(published_at) if published_at else None
                days_since_upload = (datetime.now(UTC) - published_at_dt).days if published_at_dt is not None else None

                row = {
                    "id": item.get("id"),
                    "title": snippet.get("title"),
                    "description": snippet.get("description"),
                    "published_At": published_at,
                    "tags": ",".join(snippet.get("tags", [])) if snippet.get("tags") else None,
                    "category_id": snippet.get("categoryId"),
                    "default_language": snippet.get("defaultLanguage"),
                    "default_audio_language": snippet.get("defaultAudioLanguage"),
                    "thumbnail_default": snippet.get("thumbnails", {}).get("default", {}).get("url"),
                    "thumbnail_high": snippet.get("thumbnails", {}).get("high", {}).get("url"),
                    "duration": content.get("duration"),
                    "view_count": stats.get("viewCount"),
                    "like_count": stats.get("likeCount"),
                    "comment_count": stats.get("commentCount"),
                    "privacy_status": status.get("privacyStatus"),
                    "channel_id": channel_info.get("channel_id"),
                    "channel_title": channel_info.get("channel_title"),
                    "channel_description": channel_info.get("channel_description"),
                    "channel_country": channel_info.get("channel_country"),
                    "channel_thumbnail": channel_info.get("channel_thumbnail"),
                    "channel_subscription": channel_info.get("channel_subscription"),
                    "channel_video_count": channel_info.get("channel_video_count"),
                }

                rows.append(row)

            print(f"Fetched details for {len(batch_ids)} videos...")

            time.sleep(0.1)
        except HttpError as e:
            print(f"⚠️ HttpError while fetching details: {e}")
            time.sleep(5)
            continue

    # Step 4: Combine & sort
    df = pd.DataFrame(rows)
    df = df.drop_duplicates(subset=["id"]).sort_values("published_At").reset_index(drop=True)
    return df

# ========================
# MAIN SCRIPT
# ========================
df_videos = get_all_videos_from_channel(API_KEY, CHANNEL_ID)

# Save CSV
df_videos.to_csv(CSV_FILE, index=False)
print(f"\n✅ Data saved to {CSV_FILE} ({len(df_videos)} videos)")

# Preview
pd.set_option("display.max_columns", None)
display(df_videos.head())


df_videos.to_csv("channel_videos_full.csv", index=False)


from google.colab import files
files.download("channel_videos_full.csv")
