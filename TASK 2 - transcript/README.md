# 🎬 YouTube Transcript Fetcher

A lightweight Python script to fetch YouTube video transcripts using the `youtube-transcript-api`.  
It reads video IDs from a CSV file, retrieves transcripts, and saves the results with transcript availability tracking.

---

## 🧠 Features

✅ Fetches English transcripts (`languages=['en']`)  
✅ Skips unavailable transcripts gracefully  
✅ Adds availability tracking for each video  
✅ Saves output in CSV format  
✅ Simple, dependency-free (only one library!)

---

## ⚙️ Requirements

Install the required library before running the script:

```bash
pip install youtube-transcript-api
