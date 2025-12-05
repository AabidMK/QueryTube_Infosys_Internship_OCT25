"""
YouTube Dataset Generator
-------------------------
Fetches all video and channel details for a given YouTube channel (e.g., Data School)
and saves them into a standardized CSV file.
"""

import requests
import pandas as pd
import time

#  Replace with your valid YouTube Data API key
API_KEY = "AIzaSyC8rzB6dGJrjF-SVmcRD27c0-NojgHO4A0"

#  Channel name to fetch
CHANNEL_NAME = "Data School"

# ============================
#  GET CHANNEL ID
# ============================
def get_channel_id(channel_name):
    """Fetch channel ID from channel name or search results."""
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": channel_name,
        "type": "channel",
        "maxResults": 1,
        "key": API_KEY
    }
    response = requests.get(url, params=params).json()
    if "items" not in response or not response["items"]:
        raise Exception("Channel not found!")
    return response["items"][0]["snippet"]["channelId"]

# ============================
#  GET CHANNEL DETAILS
# ============================
def get_channel_details(channel_id):
    """Fetch full channel details."""
    url = "https://www.googleapis.com/youtube/v3/channels"
    params = {
        "part": "snippet,statistics",
        "id": channel_id,
        "key": API_KEY
    }
    data = requests.get(url, params=params).json()["items"][0]
    snip = data["snippet"]
    stats = data["statistics"]

    channel_info = {
        "channel_id": channel_id,
        "channel_title": snip.get("title"),
        "channel_description": snip.get("description"),
        "channel_country": snip.get("country"),
        "channel_thumbnail": snip["thumbnails"]["default"]["url"],
        "channel_subscriberCount": stats.get("subscriberCount"),
        "channel_videoCount": stats.get("videoCount")
    }
    return channel_info

# ============================
#  GET ALL VIDEO IDS
# ============================
def get_all_video_ids(channel_id):
    """Fetch all video IDs uploaded by a channel."""
    video_ids = []
    next_page_token = None
    print(" Fetching all video IDs...")

    while True:
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "id",
            "channelId": channel_id,
            "maxResults": 50,
            "order": "date",
            "pageToken": next_page_token,
            "type": "video",
            "key": API_KEY
        }
        response = requests.get(url, params=params).json()
        video_ids += [item["id"]["videoId"] for item in response.get("items", [])]

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break
        time.sleep(0.1)  # avoid rate limit

    print(f" Found {len(video_ids)} videos.")
    return video_ids

# ============================
# 4️⃣ GET VIDEO DETAILS
# ============================
def get_video_details(video_ids, channel_info):
    """Fetch details for each video ID and combine with channel info."""
    videos_data = []
    print(" Fetching video details...")

    for i in range(0, len(video_ids), 50):  # YouTube API allows max 50 IDs per call
        url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            "part": "snippet,contentDetails,statistics,status",
            "id": ",".join(video_ids[i:i+50]),
            "key": API_KEY
        }
        response = requests.get(url, params=params).json()

        for item in response.get("items", []):
            snip = item["snippet"]
            stats = item.get("statistics", {})
            cont = item.get("contentDetails", {})
            status = item.get("status", {})

            videos_data.append({
                **channel_info,
                "video_id": item["id"],
                "video_title": snip.get("title"),
                "video_description": snip.get("description"),
                "publishedAt": snip.get("publishedAt"),
                "tags": ",".join(snip.get("tags", [])) if snip.get("tags") else None,
                "categoryId": snip.get("categoryId"),
                "defaultLanguage": snip.get("defaultLanguage"),
                "defaultAudioLanguage": snip.get("defaultAudioLanguage"),
                "thumbnail_url": snip["thumbnails"]["default"]["url"],
                "duration": cont.get("duration"),
                "viewCount": stats.get("viewCount"),
                "likeCount": stats.get("likeCount"),
                "commentCount": stats.get("commentCount"),
                "privacyStatus": status.get("privacyStatus")
            })

        time.sleep(0.2)  # polite delay to avoid quota issues

    print(f" Collected data for {len(videos_data)} videos.")
    return videos_data

# ============================
#  SAVE TO CSV
# ============================
def save_to_csv(data, filename="dataschool_dataset.csv"):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f" Data saved to {filename}")

# ============================
#  RUN EVERYTHING
# ============================
if __name__ == "__main__":
    print("Starting YouTube data extraction...")

    channel_id = get_channel_id(CHANNEL_NAME)
    channel_info = get_channel_details(channel_id)
    video_ids = get_all_video_ids(channel_id)
    videos_data = get_video_details(video_ids, channel_info)

    save_to_csv(videos_data)
    print(" Task completed successfully!")
