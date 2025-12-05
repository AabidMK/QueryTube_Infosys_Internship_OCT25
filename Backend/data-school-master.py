import pandas as pd
import re
import isodate # You may need to install this: pip install isodate

# --- Configuration ---
# Use the output from the previous step as input
INPUT_CSV_PATH = "dataschool_transcripts_video_metadata.csv" 
OUTPUT_CSV_PATH = "master_dataset.csv"

# --- Helper Functions ---

def clean_text(text):
    """Converts text to lowercase and removes special characters."""
    # Convert to string first to handle potential NaN/float values
    text = str(text)
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters (keep only letters, numbers, and whitespace)
    # This regex will remove punctuation, symbols, etc.
    text = re.sub(r'[^a-z0-9\s]', '', text)
    
    # Optional: Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def convert_iso_duration_to_seconds(iso_duration):
    """Converts ISO 8601 duration (e.g., PT1M30S) to total seconds."""
    try:
        # Parse the ISO 8601 duration string
        duration_obj = isodate.parse_duration(iso_duration)
        # Return the total duration in seconds
        return duration_obj.total_seconds()
    except (isodate.ISO8601Error, TypeError):
        # Handle errors or missing (NaN) values
        return None

# --- Main Script ---

print(f"Loading dataset from: {INPUT_CSV_PATH}")
try:
    df = pd.read_csv(INPUT_CSV_PATH)
except FileNotFoundError:
    print(f"❌ Error: Input file not found at '{INPUT_CSV_PATH}'.")
    exit()

print("Standardizing data...")

# 1. Standardize 'video_title' column
# (This was already done, but running again ensures consistency)
df['video_title'] = df['video_title'].apply(clean_text)

# 2. Standardize 'transcript' column
# (This column is currently empty, but this will clean it if it had data)
df['transcript'] = df['transcript'].apply(clean_text)

# 3. Convert 'duration' column to 'duration_seconds'
# This creates/overwrites 'duration_seconds' using the original 'duration' column
df['duration_seconds'] = df['duration'].apply(convert_iso_duration_to_seconds)

print("\nCleaning complete. Final DataFrame preview:")
print(df[['video_title', 'duration', 'duration_seconds', 'transcript']].head())

# 4. Save the final standardized DataFrame
df.to_csv(OUTPUT_CSV_PATH, index=False, encoding='utf-8')

print(f"\n✅ Successfully saved standardized data to: {OUTPUT_CSV_PATH}")