import pandas as pd
import re
from datetime import timedelta

# Load the CSV data
df = pd.read_csv('videos_with_transcripts_updated.csv')

# Function to clean text (remove special characters and convert to lowercase)
def clean_text(text):
    if pd.isna(text):
        return ""
    # Remove special characters except spaces, keep alphanumeric and basic punctuation
    cleaned = re.sub(r'[^\w\s]', '', str(text))
    # Convert to lowercase
    return cleaned.lower()

# Function to convert ISO 8601 duration to seconds
def duration_to_seconds(duration):
    if pd.isna(duration):
        return 0
    
    # Remove PT prefix
    duration = duration.replace('PT', '')
    
    total_seconds = 0
    
    # Extract hours
    if 'H' in duration:
        hours = duration.split('H')[0]
        total_seconds += int(hours) * 3600
        duration = duration.split('H')[1] if 'H' in duration else duration
    
    # Extract minutes
    if 'M' in duration:
        minutes = duration.split('M')[0]
        total_seconds += int(minutes) * 60
        duration = duration.split('M')[1] if 'M' in duration else duration
    
    # Extract seconds
    if 'S' in duration:
        seconds = duration.split('S')[0]
        total_seconds += int(seconds)
    
    return total_seconds

# Apply cleaning to titles and transcripts
df['title_x_clean'] = df['title_x'].apply(clean_text)
df['title_y_clean'] = df['title_y'].apply(clean_text)
df['transcript_clean'] = df['transcript'].apply(clean_text)

# Convert duration to seconds
df['duration_seconds'] = df['duration'].apply(duration_to_seconds)

# Display the cleaned data
print("Original and Cleaned Data:")
print("=" * 80)
for idx, row in df.iterrows():
    print(f"\nVideo {idx + 1}:")
    print(f"Original Title: {row['title_x']}")
    print(f"Cleaned Title: {row['title_x_clean']}")
    print(f"Original Duration: {row['duration']}")
    print(f"Duration in Seconds: {row['duration_seconds']}")
    print(f"Transcript available: {row['is_transcript_available']}")
    if row['is_transcript_available'] and len(row['transcript_clean']) > 0:
        transcript_preview = row['transcript_clean'][:100] + "..." if len(row['transcript_clean']) > 100 else row['transcript_clean']
        print(f"Transcript Preview: {transcript_preview}")
    print("-" * 50)

# Summary statistics
print(f"\nSummary Statistics:")
print(f"Total videos: {len(df)}")
print(f"Videos with transcripts: {df['is_transcript_available'].sum()}")
print(f"Average duration: {df['duration_seconds'].mean():.2f} seconds")
print(f"Total duration: {df['duration_seconds'].sum()} seconds")

# Show duration conversion examples
print(f"\nDuration Conversion Examples:")
for idx, row in df.iterrows():
    print(f"{row['duration']} -> {row['duration_seconds']} seconds")