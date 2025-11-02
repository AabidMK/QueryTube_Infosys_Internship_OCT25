import pandas as pd
import re

def clean_text(text):
    """
    Remove special characters and convert to lowercase
    """
    if pd.isna(text):
        return ""
    
    # Convert to string if not already
    text = str(text)
    
    # Remove special characters except alphanumeric and basic punctuation
    cleaned = re.sub(r'[^\w\s\.\,\!\?\-]', '', text)
    
    # Convert to lowercase
    cleaned = cleaned.lower()
    
    return cleaned.strip()

def convert_duration_to_seconds(duration):
    """
    Convert ISO 8601 duration format to seconds
    """
    if pd.isna(duration):
        return 0
    
    duration = str(duration)
    
    # Pattern to match ISO 8601 duration format (PT#H#M#S)
    pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
    match = re.match(pattern, duration)
    
    if not match:
        return 0
    
    hours = int(match.group(1)) if match.group(1) else 0
    minutes = int(match.group(2)) if match.group(2) else 0
    seconds = int(match.group(3)) if match.group(3) else 0
    
    total_seconds = hours * 3600 + minutes * 60 + seconds
    return total_seconds

def process_file(input_file, output_file=None):
    """
    Process the file to standardize titles, transcripts, and duration
    """
    # Read the file (supports CSV, Excel, JSON)
    if input_file.endswith('.csv'):
        df = pd.read_csv(input_file)
    elif input_file.endswith('.xlsx'):
        df = pd.read_excel(input_file)
    elif input_file.endswith('.json'):
        df = pd.read_json(input_file)
    else:
        raise ValueError("Unsupported file format. Use CSV, Excel, or JSON.")
    
    print(f"Original data shape: {df.shape}")
    
    # Store original values for comparison
    original_title = df['title'].copy() if 'title' in df.columns else None
    original_transcript = df['transcript'].copy() if 'transcript' in df.columns else None
    original_duration = df['duration'].copy() if 'duration' in df.columns else None
    
    # Standardize titles (update existing column)
    if 'title' in df.columns:
        df['title'] = df['title'].apply(clean_text)
        print("Titles standardized successfully")
    
    # Standardize transcripts (update existing column)
    if 'transcript' in df.columns:
        df['transcript'] = df['transcript'].apply(clean_text)
        print("Transcripts standardized successfully")
    
    # Convert duration to seconds (update existing column)
    if 'duration' in df.columns:
        df['duration'] = df['duration'].apply(convert_duration_to_seconds)
        print("Duration converted to seconds successfully")
    
    # Save the processed file
    if output_file:
        if output_file.endswith('.csv'):
            df.to_csv(output_file, index=False)
        elif output_file.endswith('.xlsx'):
            df.to_excel(output_file, index=False)
        elif output_file.endswith('.json'):
            df.to_json(output_file, orient='records', indent=2)
        
        print(f"Processed file saved as: {output_file}")
    
    return df, original_title, original_transcript, original_duration

def display_sample_results(df, original_title=None, original_transcript=None, original_duration=None):
    """
    Display sample results for verification
    """
    print("\n" + "="*50)
    print("SAMPLE RESULTS (BEFORE & AFTER)")
    print("="*50)
    
    if 'title' in df.columns and original_title is not None:
        print("\nTitle Samples:")
        for i in range(min(3, len(df))):
            print(f"{i+1}. Before: {original_title.iloc[i]}")
            print(f"   After:  {df['title'].iloc[i]}")
            print()
    
    if 'transcript' in df.columns and original_transcript is not None:
        print("\nTranscript Samples (first 100 chars):")
        for i in range(min(2, len(df))):
            before_preview = str(original_transcript.iloc[i])[:100] + "..." if len(str(original_transcript.iloc[i])) > 100 else str(original_transcript.iloc[i])
            after_preview = str(df['transcript'].iloc[i])[:100] + "..." if len(str(df['transcript'].iloc[i])) > 100 else str(df['transcript'].iloc[i])
            print(f"{i+1}. Before: {before_preview}")
            print(f"   After:  {after_preview}")
            print()
    
    if 'duration' in df.columns and original_duration is not None:
        print("\nDuration Conversion Samples:")
        for i in range(min(5, len(df))):
            print(f"{i+1}. {original_duration.iloc[i]} -> {df['duration'].iloc[i]} seconds")

# Main execution
if __name__ == "__main__":
    # Configuration
    input_filename = "master_dataset_updated.csv"  # Change this to your actual file name
    output_filename = "processed_file.csv"  # Change desired output name
    
    try:
        # Process the file
        processed_df, orig_title, orig_transcript, orig_duration = process_file(input_filename, output_filename)
        
        # Display sample results
        display_sample_results(processed_df, orig_title, orig_transcript, orig_duration)
        
        # Print summary statistics
        print("\n" + "="*50)
        print("SUMMARY STATISTICS")
        print("="*50)
        
        if 'duration' in processed_df.columns:
            print(f"Duration Statistics (seconds):")
            print(f"  Min: {processed_df['duration'].min()}")
            print(f"  Max: {processed_df['duration'].max()}")
            print(f"  Mean: {processed_df['duration'].mean():.2f}")
            print(f"  Total videos: {len(processed_df)}")
        
    except FileNotFoundError:
        print(f"Error: File '{input_filename}' not found.")
        print("Please make sure the file exists in the current directory.")
    except Exception as e:
        print(f"Error processing file: {str(e)}")