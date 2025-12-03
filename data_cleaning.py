import pandas as pd
import re
from datetime import timedelta

# --- File Configuration ---
input_file = " INPUT_FILE_PATH"
output_file = "OUTPUT FILE PATH" # New output file name

# 1. Load Data
try:
    df = pd.read_csv(input_file)
    print(f"Successfully loaded {input_file}.")
except FileNotFoundError:
    print(f"ERROR: Input file '{input_file}' not found. Please ensure the file is present.")
    exit()

# --- 2. Standardize Titles and Transcripts (In-place) ---
print("Starting standardization of 'title' and 'transcript' (overwriting original columns)...")

def clean_text(text):
    """Removes special characters, converts to lowercase, and strips extra spaces."""
    if pd.isna(text) or text is None:
        return ""
    text = str(text)
    # 1. Remove non-alphanumeric characters, keeping spaces
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    # 2. Convert to lowercase
    text = text.lower()
    # 3. Remove extra whitespaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Overwrite original columns using the corrected lowercase names: 'title' and 'transcript'
df['title'] = df['title'].apply(clean_text)
df['transcript'] = df['transcript'].apply(clean_text)

print("Text standardization complete. 'title' and 'transcript' columns have been overwritten.")


# --- 3. Convert Duration (ISO 8601) to Seconds (In-place) ---
# Using the corrected lowercase column name 'duration'
duration_col_iso = 'duration' 

def iso_to_seconds(iso_duration):
    """Converts ISO 8601 duration string (e.g., PT16M26S) to total seconds."""
    if pd.isna(iso_duration) or not iso_duration:
        return 0
    
    duration = iso_duration.replace('PT', '')
    total_seconds = 0
    
    # Pattern to find H (Hours), M (Minutes), S (Seconds)
    hours = re.search(r'(\d+)H', duration)
    minutes = re.search(r'(\d+)M', duration)
    seconds = re.search(r'(\d+)S', duration)
    
    if hours:
        total_seconds += int(hours.group(1)) * 3600
    if minutes:
        total_seconds += int(minutes.group(1)) * 60
    if seconds:
        total_seconds += int(seconds.group(1))
        
    return total_seconds

# Overwrite the original duration column with seconds
if duration_col_iso in df.columns:
    df[duration_col_iso] = df[duration_col_iso].apply(iso_to_seconds)
    print(f"Duration conversion complete. '{duration_col_iso}' column now contains duration in seconds.")
else:
    print(f"WARNING: Duration column '{duration_col_iso}' not found. Skipping duration conversion.")


# --- 4. Save the Cleaned DataFrame ---
df.to_csv(output_file, index=False)

print(f"\n--- Data Standardization Complete ---")
print(f"Original columns were overwritten and the updated data saved to {output_file}.")
print("\nFirst 5 rows of Title and Duration for verification (values are now cleaned text and seconds):")
print(df[['title', 'transcript', duration_col_iso]].head())