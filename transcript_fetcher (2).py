from youtube_transcript_api import YouTubeTranscriptApi
import pandas as pd
import time
import os

def fetch_transcript_for_video(video_id):
    """Fetch transcript for a single video"""
    try:
        api = YouTubeTranscriptApi()
        transcript_result = api.fetch(video_id, languages=['en'])
        snippets = transcript_result.snippets
        full_text = ' '.join([snippet.text for snippet in snippets])
        
        # Clean up the text (remove extra spaces from line breaks)
        cleaned_text = ' '.join(full_text.split())
        
        print(f"✅ Successfully fetched transcript for: {video_id}")
        print(f"   Snippets: {len(snippets)}, Characters: {len(cleaned_text)}")
        
        return cleaned_text
        
    except Exception as e:
        print(f"❌ Failed to fetch transcript for {video_id}: {str(e)}")
        return None

def process_video_transcripts(csv_file_path, batch_size=10, delay=1):
    """Process all videos from CSV file and save results"""
    try:
        # Read CSV file
        df = pd.read_csv(csv_file_path)
        
        # Check if videoId column exists
        if 'videoId' not in df.columns:
            print("❌ Error: 'videoId' column not found in CSV file")
            print(f"Available columns: {list(df.columns)}")
            return None
        
        video_ids = df['videoId'].tolist()
        
        print(f"📁 Loaded {len(video_ids)} video IDs from {csv_file_path}")
        print(f"🔄 Starting transcript fetching...")
        
        # Fetch transcripts
        transcripts = []
        successful = 0
        failed = 0
        
        for i, video_id in enumerate(video_ids, 1):
            print(f"\n📹 Processing {i}/{len(video_ids)}: {video_id}")
            
            transcript = fetch_transcript_for_video(video_id)
            transcripts.append(transcript)
            
            if transcript:
                successful += 1
            else:
                failed += 1
            
            # Add delay to avoid rate limiting (be nice to YouTube's servers)
            if i < len(video_ids):  # No delay after the last one
                print(f"⏳ Waiting {delay} second(s)...")
                time.sleep(delay)
            
            # Optional: Save progress every batch_size videos
            if i % batch_size == 0:
                print(f"💾 Progress: {i}/{len(video_ids)} videos processed")
        
        # Add transcripts to dataframe
        df['transcript'] = transcripts
        
        # Calculate success rate
        success_rate = (successful / len(video_ids)) * 100
        
        print(f"\n{'='*50}")
        print(f"📊 PROCESSING COMPLETE!")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success rate: {success_rate:.1f}%")
        print(f"{'='*50}")
        
        # Save results
        output_file = csv_file_path.replace('.csv', '_with_transcripts.csv')
        df.to_csv(output_file, index=False)
        print(f"💾 Saved results to: {output_file}")
        
        # Save a summary file
        summary_file = csv_file_path.replace('.csv', '_summary.txt')
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"Transcript Processing Summary\n")
            f.write(f"=============================\n")
            f.write(f"Source CSV: {csv_file_path}\n")
            f.write(f"Total videos: {len(video_ids)}\n")
            f.write(f"Successful: {successful}\n")
            f.write(f"Failed: {failed}\n")
            f.write(f"Success rate: {success_rate:.1f}%\n")
            f.write(f"Output file: {output_file}\n")
        
        print(f"📝 Summary saved to: {summary_file}")
        
        return df
        
    except Exception as e:
        print(f"❌ Error processing CSV: {str(e)}")
        return None

def preview_csv_structure(csv_file_path):
    """Preview the CSV file structure"""
    try:
        df = pd.read_csv(csv_file_path)
        print(f"📋 CSV Structure Preview for: {csv_file_path}")
        print(f"   Shape: {df.shape} (rows: {df.shape[0]}, columns: {df.shape[1]})")
        print(f"   Columns: {list(df.columns)}")
        print(f"   First few video IDs: {df['videoId'].head().tolist()}")
        return df.head()
    except Exception as e:
        print(f"❌ Error reading CSV: {str(e)}")
        return None

# MAIN EXECUTION
if __name__ == "__main__":
    # Specify your CSV file path
    csv_file_path = "videos.csv"  # Change this to your actual CSV file path
    
    # Check if file exists
    if not os.path.exists(csv_file_path):
        print(f"❌ File not found: {csv_file_path}")
        print("Please make sure your CSV file exists in the same directory.")
    else:
        # First, preview the CSV structure
        print("🔍 Previewing CSV structure...")
        preview = preview_csv_structure(csv_file_path)
        
        if preview is not None:
            print("\n" + "="*60)
            response = input("Proceed with transcript fetching? (y/n): ")
            
            if response.lower() in ['y', 'yes']:
                print("\n🚀 Starting transcript fetching process...")
                result_df = process_video_transcripts(
                    csv_file_path, 
                    batch_size=10, 
                    delay=1  # 1 second delay between requests
                )
                
                if result_df is not None:
                    print(f"\n🎉 All done! Check the output files for results.")
            else:
                print("❌ Process cancelled by user.")
               