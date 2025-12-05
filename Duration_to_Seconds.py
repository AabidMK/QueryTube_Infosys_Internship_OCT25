import pandas as pd
import isodate

# --- Load your dataset ---
# Replace with your actual CSV file name
df = pd.read_csv("master_dataset_updated.csv")

# --- Convert ISO 8601 duration to seconds ---
def convert_duration_to_seconds(duration_str):
    try:
        return isodate.parse_duration(duration_str).total_seconds()
    except Exception:
        return None  # In case of missing or invalid data

# Apply the conversion
df["duration_seconds"] = df["duration"].apply(convert_duration_to_seconds)

# --- Save the updated dataset ---
df.to_csv("master_dataset_with_duration_seconds.csv", index=False)

print("✅ Conversion complete! File saved as 'master_dataset_with_duration_seconds.csv'")