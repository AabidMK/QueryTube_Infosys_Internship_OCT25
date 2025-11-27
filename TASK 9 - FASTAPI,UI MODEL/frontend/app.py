import streamlit as st
import requests
import pandas as pd

FASTAPI_URL = "http://127.0.0.1:8000"

st.title("🎬 YouTube Vector Search UI")

# ============================================================
# Helper: Summarize transcript of each video
# ============================================================
def summarize_text(text, max_sentences=2):
    if not text or len(text.strip()) == 0:
        return "No transcript available."

    sentences = text.split(". ")
    return ". ".join(sentences[:max_sentences]) + ("." if not sentences[0].endswith(".") else "")

# ============================================================
# 1️⃣ Upload CSV & Ingest
# ============================================================
st.subheader("📤 Upload CSV for ingestion")
csv_file = st.file_uploader("Upload CSV file", type=["csv"])

if csv_file:
    if st.button("Ingest"):
        files = {"file": csv_file}
        response = requests.post(f"{FASTAPI_URL}/ingest", files=files)

        if response.status_code == 200:
            st.success("✅ Ingestion completed successfully")
        else:
            st.error(f"❌ Backend Error: {response.text}")

# ============================================================
# 2️⃣ Search Section
# ============================================================
st.subheader("🔍 Search Videos")

query = st.text_input("Enter your search query")
k = st.slider("Number of search results", 1, 20, 5)

if st.button("Search"):
    if query.strip() == "":
        st.error("⚠️ Enter a valid query")
    else:
        params = {"query": query, "k": k}
        response = requests.get(f"{FASTAPI_URL}/search", params=params)

        if response.status_code != 200:
            st.error(f"❌ Error from backend: {response.text}")
        else:
            data = response.json()
            results = data.get("results", [])
            summary = data.get("summary", "No summary available")

            if not results:
                st.warning("No results found.")
            else:
                # Display Summary
                st.subheader("📝 Overall Summary")
                st.write(summary)

                # Display Results Table
                df = pd.DataFrame(results)
                st.subheader("📊 Results Table")
                st.dataframe(df)

                # Card-style output with video + individual summaries
                st.subheader("🎥 Video Results")
                st.markdown("---")

                for item in results:
                    video_url = f"https://www.youtube.com/watch?v={item['video_id']}"

                    st.markdown(f"## {item['rank']}. **{item['title']}**")
                    st.video(video_url)

                    # Individual summary
                    individual_summary = summarize_text(item.get("transcript", ""))

                    st.markdown(f"""
                    **Channel:** {item['channel']}  
                    **Similarity Score:** `{item['similarity_score']}`  

                    ### 📝 Video Summary
                    {individual_summary}
                    """)

                    st.markdown("---")