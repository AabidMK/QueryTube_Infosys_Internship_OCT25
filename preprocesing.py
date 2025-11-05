import pandas as pd
import re

# Load the CSV file
df = pd.read_csv("master_dataset_updated.csv")

# Display the first few rows
df.head()

# Function to clean text
def clean_text(text):
    if pd.isnull(text):
        return ""
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)  # keep only alphanumeric and spaces
    return text.lower().strip()

# Apply cleaning to relevant columns
df['title'] = df['title'].apply(clean_text)
df['transcript'] = df['transcript'].apply(clean_text)


import isodate

def convert_duration_to_seconds(duration):
    try:
        td = isodate.parse_duration(duration)
        return int(td.total_seconds())
    except:
        return None

df['duration_seconds'] = df['duration'].apply(convert_duration_to_seconds)

output_file = "cleaned_master_youtube_data.csv"
df.to_csv(output_file, index=False)
print(f"✅ Cleaned CSV saved as {output_file}")