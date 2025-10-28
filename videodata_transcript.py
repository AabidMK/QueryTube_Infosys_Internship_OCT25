import pandas as pd

# Read the CSV file
df = pd.read_csv('videos_with_transcripts.csv')

# Add the new column
df['is_transcript_available'] = df['transcript'].notna() & (df['transcript'].str.strip() != '')

# Save the updated dataset
df.to_csv('videos_with_transcripts_updated.csv', index=False)

print(f"Total videos: {len(df)}")
print(f"Videos with transcripts: {df['is_transcript_available'].sum()}")
print(f"Videos without transcripts: {len(df) - df['is_transcript_available'].sum()}")