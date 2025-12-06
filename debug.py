# debug_ids.py
import chromadb

print("🔍 DEBUG: Checking database IDs")

try:
    # Connect to database
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_collection("youtube_videos")
    
    # Get count
    count = collection.count()
    print(f"Total videos: {count}")
    
    # Get all IDs
    all_data = collection.get()
    all_ids = all_data['ids']
    
    print(f"\nFirst 20 IDs:")
    for i, vid_id in enumerate(all_ids[:20], 1):
        print(f"{i:2}. {vid_id}")
    
    # Check for the problematic ID
    target_id = "mmIidOoHCfs"
    print(f"\nLooking for ID: '{target_id}'")
    
    if target_id in all_ids:
        print(f"✅ FOUND: {target_id}")
        # Get the video details
        video = collection.get(ids=[target_id])
        metadata = video['metadatas'][0]
        print(f"Title: {metadata['title']}")
        print(f"Channel: {metadata['channel_title']}")
        print(f"Views: {metadata['view_count']}")
    else:
        print(f"❌ NOT FOUND: {target_id}")
        
        # Look for similar IDs
        print("\nLooking for similar IDs...")
        similar = [id for id in all_ids if target_id.lower() in id.lower() or id.lower() in target_id.lower()]
        if similar:
            print(f"Found {len(similar)} similar IDs:")
            for id in similar:
                print(f"  - {id}")
        else:
            # Check case variations
            lower_ids = [id.lower() for id in all_ids]
            if target_id.lower() in lower_ids:
                idx = lower_ids.index(target_id.lower())
                print(f"Found with different case: {all_ids[idx]}")
    
    # Show IDs from the CSV that we know exist
    print("\n\nIDs from your CSV (first 10):")
    import pandas as pd
    df = pd.read_csv('dataset_with_embeddings.csv')
    for i, row in df.head(10).iterrows():
        print(f"{i+1:2}. {row['id']} - {row['title'][:50]}...")
        
except Exception as e:
    print(f"Error: {e}")