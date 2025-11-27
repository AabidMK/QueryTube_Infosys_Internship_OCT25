# 🔍 YouTube Video Search Engine using FAISS, TF-IDF & SVD

This project implements a semantic search system for YouTube video
transcripts. It uses **FAISS** for fast similarity search, **TF-IDF +
SVD** for text-based embeddings, and a **CSV dataset** containing video
details with precomputed embeddings.

------------------------------------------------------------------------



## ⚙️ Features

✅ Load and parse YouTube video metadata and embeddings from CSV\
✅ Build a FAISS vector index for fast similarity lookup\
✅ Create TF-IDF + SVD models for text-based search representation\
✅ Perform semantic search on video titles and transcripts\
✅ Display ranked results with similarity scores

------------------------------------------------------------------------

## 🧠 How It Works

### 1. Load Data

-   Reads the CSV file containing video metadata and embeddings.
-   Parses the embedding strings into numerical vectors.

### 2. Build Index

-   Uses `faiss.IndexFlatL2` to store and search embedding vectors.

### 3. Text Modeling

-   Combines video title and transcript text.
-   Uses `TfidfVectorizer` to represent text numerically.
-   Applies `TruncatedSVD` for dimensionality reduction.

### 4. Search Query

-   Converts the search query into an embedding using TF-IDF + SVD.
-   Searches for the most similar video embeddings in the FAISS index.
-   Displays the top 5 most relevant videos ranked by similarity.

------------------------------------------------------------------------

## 🧩 Requirements

Install the required Python libraries using:

``` bash
pip install pandas numpy faiss-cpu scikit-learn
```

------------------------------------------------------------------------

## 📄 CSV Format

The CSV file must contain the following columns:

  Column Name      Description
  ---------------- ----------------------------------
  video_id         Unique ID of the video
  title            Title of the YouTube video
  channel_title    Channel name
  transcript       Transcript text of the video
  text_embedding   List of numeric embedding values

### Example row:

    video_id,title,channel_title,transcript,text_embedding
    abc123,Deep Learning Explained,AI Channel,"Welcome to the course...",[0.12, 0.98, 0.34, ...]

------------------------------------------------------------------------

## 🚀 How to Run

1.  Place your `youtube_details_with_embeddings.csv` file in the project
    directory.\
2.  Run the script:

``` bash
python search_videos.py
```

3.  Enter your search query, for example:

```{=html}
<!-- -->
```
    Enter your search query (or type 'exit' to quit): machine learning basics

### Example output:

    🔍 Top 5 Most Relevant Videos:

    Rank 1
    Video ID: abc123
    Title: Machine Learning Basics Explained
    Channel: Tech with AI
    Similarity Score: 0.8345
    ------------------------------------------------------------
    Rank 2
    Video ID: xyz456
    Title: Introduction to AI
    Channel: Data School
    Similarity Score: 0.7812
    ------------------------------------------------------------

Type `exit` to quit the program.

------------------------------------------------------------------------

## 🧾 Notes

-   Make sure your embeddings column (`text_embedding`) is a valid list
    or JSON array.
-   The FAISS index uses **L2 distance**; similarity is computed as
    `1 / (1 + distance)`.
-   You can adjust `k` in the search function to get more or fewer
    results.

------------------------------------------------------------------------

## 🧑‍💻 Author

**Developed by:** M Shalom Vishal\
**Technologies:** Python, FAISS, Scikit-learn, Pandas, NumPy\
**Use Case:** Semantic video search system for YouTube metadata and
transcripts
