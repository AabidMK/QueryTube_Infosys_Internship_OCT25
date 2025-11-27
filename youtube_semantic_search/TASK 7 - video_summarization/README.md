# 🎥 YouTube Video Summarizer using FAISS and Google Gemini

## 📘 Overview

This project summarizes YouTube video transcripts efficiently using
**FAISS** for fast retrieval and **Google Gemini** for generating
structured summaries.\
It reads transcript embeddings from a CSV, builds a FAISS index,
retrieves relevant transcripts using a video ID, and uses Gemini to
summarize them.

------------------------------------------------------------------------

## ⚙️ Features

-   ✅ Build and store FAISS vector index from transcript embeddings.
-   🔍 Retrieve transcript using video ID.
-   🧠 Summarize transcript using Google Gemini API.
-   💾 Automatically skip index rebuild if already exists.

------------------------------------------------------------------------

## 🧩 Dependencies

Make sure to install the following Python packages:

``` bash
pip install pandas numpy faiss-cpu google-generativeai
```

------------------------------------------------------------------------

## 🚀 How to Run

1.  Place your CSV file with embeddings (e.g.,
    `youtube_details_with_embeddings.csv`) in the project folder.

2.  Run the script using:

    ``` bash
    python summarize_video.py
    ```

3.  Enter the YouTube Video ID when prompted.

4.  The Gemini API will generate a clean summary for the transcript.

------------------------------------------------------------------------

## 🧠 CSV Format Example

Your CSV file should have the following columns:

  ------------------------------------------------------------------------
  video_id            transcript              text_embedding
  ------------------- ----------------------- ----------------------------
  abc123              This is a sample        \[0.12, 0.23, 0.56, ...\]
                      transcript text...      

  ------------------------------------------------------------------------

------------------------------------------------------------------------

## 🔑 API Key

Replace the placeholder `GEMINI_API_KEY` with your actual **Google
Gemini API Key**.

``` python
GEMINI_API_KEY = "YOUR_API_KEY_HERE"
```

------------------------------------------------------------------------

## 📦 Output Example

``` text
🎬 ====== VIDEO SUMMARY ======
This video discusses the main ideas of machine learning models, including supervised and unsupervised learning...
```

------------------------------------------------------------------------

## 📁 File Structure

    📂 youtube-summarizer/
    │── youtube_details_with_embeddings.csv
    │── youtube_faiss.index
    │── summarize_video.py
    │── README.pdf

------------------------------------------------------------------------

## 🧾 Author

Developed by **M Shalom Vishal**
