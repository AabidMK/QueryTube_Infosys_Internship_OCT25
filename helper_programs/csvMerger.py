import streamlit as st
import pandas as pd

# -------------------------------
# Streamlit Page Setup
# -------------------------------
st.set_page_config(page_title="📊 Merge Channel & Transcript Data", page_icon="🔗")

st.title("📊 YouTube Channel + Transcript Merger")
st.write("Upload your **Channel Analysis** and **Transcript** files to combine them into one dataset.")

# -------------------------------
# File Uploaders
# -------------------------------
channel_file = st.file_uploader("📁 Upload Channel Analysis File (Excel/CSV)", type=["csv", "xlsx"])
transcript_file = st.file_uploader("📄 Upload Transcript File (Excel/CSV)", type=["csv", "xlsx"])

# -------------------------------
# Merge Logic
# -------------------------------
if channel_file and transcript_file:
    # Read Channel File
    if channel_file.name.endswith(".csv"):
        channel_df = pd.read_csv(channel_file)
    else:
        channel_df = pd.read_excel(channel_file)

    # Read Transcript File
    if transcript_file.name.endswith(".csv"):
        transcript_df = pd.read_csv(transcript_file)
    else:
        transcript_df = pd.read_excel(transcript_file)

    st.subheader("📊 Preview of Channel Data")
    st.dataframe(channel_df.head())

    st.subheader("📝 Preview of Transcript Data")
    st.dataframe(transcript_df.head())

    # -------------------------------
    # Merge on id = video_id
    # -------------------------------
    st.info("Merging datasets... please wait.")
    merged_df = pd.merge(
        channel_df,
        transcript_df,
        how="left",
        left_on="id",
        right_on="video_id"
    )

    # Drop redundant 'video_id' column if desired
    if "video_id" in merged_df.columns:
        merged_df.drop(columns=["video_id"], inplace=True)

    # -------------------------------
    # Add transcript availability flag
    # -------------------------------
    merged_df["is_transcript_available"] = merged_df["transcript"].apply(
        lambda x: True if pd.notna(x) and isinstance(x, str) and len(x.strip()) > 0 else False
    )

    # -------------------------------
    # Show merged data
    # -------------------------------
    st.success("✅ Datasets merged successfully!")
    st.dataframe(merged_df.head())

    # -------------------------------
    # Download merged CSV
    # -------------------------------
    csv_data = merged_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Merged Dataset (CSV)",
        data=csv_data,
        file_name="merged_youtube_dataset.csv",
        mime="text/csv"
    )

else:
    st.info("⬆️ Please upload both files to proceed.")
