# 🎬 YouTube Channel Data Fetcher

A **Streamlit web app** that allows you to fetch **YouTube channel details** and **recent video data** using the **YouTube Data API v3**.  
You can easily enter a YouTube Channel ID, specify the number of videos to fetch, and download all results as a CSV file.

---

## 🚀 Features
- Fetches YouTube channel details (title, description, subscriber count, video count, etc.)
- Retrieves metadata for recent videos (title, tags, duration, views, likes, comments, etc.)
- Displays results in an interactive Streamlit table
- Exports all fetched video data as a downloadable CSV file

---

## 🧠 Technologies Used
- **Streamlit** – for the web app UI  
- **Requests** – to call the YouTube Data API  
- **Pandas** – to process and export CSV data  
- **YouTube Data API v3**

---

## ⚙️ Setup Instructions

### 1 Install Dependencies
```bash
pip install streamlit pandas requests
```

### 2 Add Your YouTube API Key
Open the Python file and replace this line with your API key:
```python
API_KEY = "YOUR_API_KEY_HERE"
```

### 3 Run the Streamlit App
```bash
streamlit run app.py
```

---

## 🧩 How It Works
1. Enter a **YouTube Channel ID** in the input field.  
2. Choose how many recent videos you want to fetch (1–200).  
3. The app fetches:
   - Channel details (name, country, description)
   - Video details (title, views, likes, comments, etc.)
4. Results are displayed in a table and can be downloaded as a CSV.

---

## 📄 Example Output (CSV Columns)
| videoId | title | publishedAt | viewCount | likeCount | commentCount | duration | tags | privacyStatus |
|----------|-------|--------------|------------|------------|----------------|-----------|------|----------------|
| x123abc | Example Video | 2025-10-25T10:00:00Z | 25000 | 900 | 120 | PT5M30S | python, streamlit | public |

---

## 🛡️ Important Notes
- The **YouTube API Key** must be valid and have YouTube Data API v3 enabled.  
- Do **not** expose your API key publicly.  
- Streamlit allows you to securely store secrets using `.streamlit/secrets.toml`.

Example:
```toml
[general]
API_KEY = "your_api_key_here"
```

---

## 👨‍💻 Author
Developed by **M Shalom Vishal**  
📧 *Feel free to use, modify, and extend this project.*

---

## 📜 License
This project is licensed under the **MIT License**.
