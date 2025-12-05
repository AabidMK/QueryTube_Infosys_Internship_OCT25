import pandas as pd
import re

# --- Load your dataset ---
df = pd.read_csv("master_dataset_with_duration_seconds.csv")
print("📋 Columns in your dataset:", df.columns.tolist())

# --- Normalize column names ---
df.columns = df.columns.str.strip().str.lower()

# --- Define cleaning function ---
def clean_transcript(text):
    if isinstance(text, str):
        # Remove all special characters except letters, numbers, and spaces
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        # Convert to lowercase and strip leading/trailing spaces
        return text.lower().strip()
    return text

# --- Find the actual transcript column ---
transcript_col = None
for col in df.columns:
    if "transcript" in col:  # handles names like 'transcript_text' or 'transcripts'
        transcript_col = col
        break

# --- Apply cleaning safely ---
if transcript_col:
    print(f"🧠 Cleaning column: '{transcript_col}'")
    df[transcript_col] = df[transcript_col].apply(clean_transcript)
else:
    print("✅ Dataset processed and saved as 'master_dataset_cleaned.csv'")
    df.to_csv("master_dataset_cleaned.csv", index=False)
    exit()

# --- Save the cleaned dataset ---
df.to_csv("master_dataset_cleaned.csv", index=False)

print("✅ Transcript cleaned and saved as 'master_dataset_cleaned.csv'")
