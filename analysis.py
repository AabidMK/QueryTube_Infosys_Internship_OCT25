import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
from urllib.parse import urlparse, parse_qs
import os
from dotenv import load_dotenv

load_dotenv()
# --------------------------
API_KEY = os.getenv("YOUTUBE_DATA_API_KEY")  # Replace with your YouTube Data API key

# YouTube API client
def get_youtube_service():
    return build("youtube", "v3", developerKey=API_KEY)

# --------------------------
def channel_analyzer():
    st.title("📺 YouTube Channel Analyzer (Detailed CSV)")

    channel_input = st.text_input("Enter YouTube Channel URL or ID:")
    max_results = st.number_input("How many latest videos to analyze?", 1, 100, 10)

    if st.button("🔍 Analyze Channel"):
        # Extract channel ID
        if "youtube.com/channel/" in channel_input:
            channel_id = channel_input.split("youtube.com/channel/")[1].split("/")[0]
        else:
            channel_id = channel_input

        youtube = get_youtube_service()

        # Get channel info
        channel_request = youtube.channels().list(
            part="snippet,statistics,contentDetails",
            id=channel_id
        )
        channel_response = channel_request.execute()
        if not channel_response["items"]:
            st.error("❌ Channel not found.")
            return

        ch_data = channel_response["items"][0]
        ch_snippet = ch_data["snippet"]
        ch_stats = ch_data["statistics"]
        uploads_playlist_id = ch_data["contentDetails"]["relatedPlaylists"]["uploads"]

        st.subheader(f"📊 Channel: {ch_snippet['title']}")
        st.image(ch_snippet["thumbnails"]["high"]["url"])
        st.write(ch_snippet["description"])
        st.write(f"**Subscribers:** {ch_stats.get('subscriberCount', 'N/A')}")
        st.write(f"**Total Views:** {ch_stats.get('viewCount', 'N/A')}")
        st.write(f"**Video Count:** {ch_stats.get('videoCount', 'N/A')}")

        # ------------------ Fetch videos ------------------
        videos = []
        next_page_token = None
        fetched = 0

        while fetched < max_results:
            playlist_req = youtube.playlistItems().list(
                part="snippet",
                playlistId=uploads_playlist_id,
                maxResults=min(50, max_results - fetched),
                pageToken=next_page_token
            )
            playlist_res = playlist_req.execute()

            for item in playlist_res["items"]:
                vid_id = item["snippet"]["resourceId"]["videoId"]
                vid_snippet = item["snippet"]

                # Get detailed video info
                vid_req = youtube.videos().list(
                    part="snippet,contentDetails,statistics,status",
                    id=vid_id
                )
                vid_res = vid_req.execute()
                if not vid_res["items"]:
                    continue
                vid_info = vid_res["items"][0]
                sn = vid_info["snippet"]
                stc = vid_info["statistics"]
                cd = vid_info["contentDetails"]
                status = vid_info["status"]

                videos.append({
                    "id": vid_id,
                    "title": sn.get("title"),
                    "description": sn.get("description"),
                    "publishedAt": sn.get("publishedAt"),
                    "tags": ",".join(sn.get("tags", [])),
                    "categoryId": sn.get("categoryId"),
                    "defaultLanguage": sn.get("defaultLanguage"),
                    "defaultAudioLanguage": sn.get("defaultAudioLanguage"),
                    "thumbnail_default": sn.get("thumbnails", {}).get("default", {}).get("url"),
                    "thumbnail_high": sn.get("thumbnails", {}).get("high", {}).get("url"),
                    "duration": cd.get("duration"),
                    "viewCount": stc.get("viewCount"),
                    "likeCount": stc.get("likeCount"),
                    "commentCount": stc.get("commentCount"),
                    "privacyStatus": status.get("privacyStatus"),
                    "channel_id": channel_id,
                    "channel_title": ch_snippet.get("title"),
                    "channel_description": ch_snippet.get("description"),
                    "channel_country": ch_snippet.get("country"),
                    "channel_thumbnail": ch_snippet.get("thumbnails", {}).get("high", {}).get("url"),
                    "channel_subscriberCount": ch_stats.get("subscriberCount"),
                    "channel_videoCount": ch_stats.get("videoCount")
                })

            fetched += len(playlist_res["items"])
            next_page_token = playlist_res.get("nextPageToken")
            if not next_page_token:
                break

        if not videos:
            st.warning("No videos found for this channel.")
            return

        df = pd.DataFrame(videos)

        st.markdown("### 📈 Latest Video Performance")
        st.dataframe(df[["title", "publishedAt", "viewCount", "likeCount", "commentCount"]])

        # Export CSV
        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Detailed CSV",
            data=csv_data,
            file_name="youtube_channel_detailed_analysis.csv",
            mime="text/csv"
        )

# --------------------------
st.sidebar.title("📊 YouTube Dashboard")
page = st.sidebar.radio("Navigate to:", ["📺 Channel Analyzer"])

if page == "📺 Channel Analyzer":
    channel_analyzer()
