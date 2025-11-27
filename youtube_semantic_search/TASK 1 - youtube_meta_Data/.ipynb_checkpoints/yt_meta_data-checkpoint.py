import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# -----------------------------
# BACKEND CONFIG
# -----------------------------
API_KEY = "AIzaSyBd_MtAx93Py2wLLXNrhicpdYR7N4wS0KY"  # Keep this secure (don’t expose in UI)

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
def get_channel_details(channel_id):
    url = f"https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&id={channel_id}&key={API_KEY}"
    res = requests.get(url).json()
    if "items" not in res or not res["items"]:
        return None

    item = res["items"][0]
    snippet = item["snippet"]
    stats = item["statistics"]

    return {
        "id": item["id"],
        "title": snippet.get("title", ""),
        "description": snippet.get("description", ""),
        "country": snippet.get("country", ""),
        "thumbnail": snippet["thumbnails"]["default"]["url"],
        "subscriberCount": stats.get("subscriberCount", 0),
        "videoCount": stats.get("videoCount", 0)
    }

def get_video_ids(channel_id, limit):
    """Fetch limited video IDs from the channel uploads playlist"""
    url = f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id={channel_id}&key={API_KEY}"
    res = requests.get(url).json()
    if "items" not in res or not res["items"]:
        return []

    playlist_id = res["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    video_ids = []
    next_page = None

    while True:
        vid_url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId={playlist_id}&maxResults=50&key={API_KEY}"
        if next_page:
            vid_url += f"&pageToken={next_page}"

        data = requests.get(vid_url).json()
        for item in data.get("items", []):
            video_ids.append(item["contentDetails"]["videoId"])
            if len(video_ids) >= limit:
                return video_ids

        next_page = data.get("nextPageToken")
        if not next_page or len(video_ids) >= limit:
            break

    return video_ids[:limit]

def get_video_details(video_ids):
    """Fetch video metadata"""
    all_videos = []
    for i in range(0, len(video_ids), 50):
        ids = ",".join(video_ids[i:i+50])
        url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails,statistics,status&id={ids}&key={API_KEY}"
        res = requests.get(url).json()

        for item in res.get("items", []):
            snippet = item["snippet"]
            stats = item.get("statistics", {})
            content = item.get("contentDetails", {})
            status = item.get("status", {})

            all_videos.append({
                "videoId": item["id"],
                "title": snippet.get("title", ""),
                "description": snippet.get("description", ""),
                "publishedAt": snippet.get("publishedAt", ""),
                "tags": ", ".join(snippet.get("tags", [])) if "tags" in snippet else "",
                "categoryId": snippet.get("categoryId", ""),
                "defaultLanguage": snippet.get("defaultLanguage", ""),
                "defaultAudioLanguage": snippet.get("defaultAudioLanguage", ""),
                "thumbnail": snippet["thumbnails"]["default"]["url"] if "thumbnails" in snippet else "",
                "duration": content.get("duration", ""),
                "viewCount": stats.get("viewCount", 0),
                "likeCount": stats.get("likeCount", 0),
                "commentCount": stats.get("commentCount", 0),
                "privacyStatus": status.get("privacyStatus", "")
            })
    return pd.DataFrame(all_videos)

# -----------------------------
# STREAMLIT UI
# -----------------------------
st.set_page_config(page_title="YouTube Channel Data Fetcher", layout="wide")
st.title("🎬 YouTube Channel Data Fetcher")

channel_id = st.text_input("Enter YouTube Channel ID")
limit = st.number_input("How many recent videos to fetch?", min_value=1, max_value=200, value=5)

if st.button("Fetch Data"):
    if channel_id:
        with st.spinner("Fetching channel and video details..."):
            channel = get_channel_details(channel_id)
            if channel:
                st.image(channel["thumbnail"], width=100)
                st.subheader(channel["title"])
                st.write(f"**Subscribers:** {channel['subscriberCount']}")
                st.write(f"**Videos:** {channel['videoCount']}")

                video_ids = get_video_ids(channel_id, limit)
                st.info(f"Fetching {len(video_ids)} videos...")

                if video_ids:
                    df = get_video_details(video_ids)
                    st.dataframe(df)

                    # Save results
                    filename = f"{channel['title'].replace(' ', '_')}_top_{limit}_videos.csv"
                    df.to_csv(filename, index=False)

                    st.success("✅ Channel data fetched successfully!")
                    st.download_button("📥 Download CSV", data=df.to_csv(index=False), file_name=filename, mime="text/csv")
            else:
                st.error("Invalid Channel ID or no data found.")
    else:
        st.warning("Please enter a channel ID.")
