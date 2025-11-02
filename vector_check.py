import pandas as pd
import chromadb
import uuid
import numpy as np
import re

def convert_tensor_string(tensor_str):
    """Convert tensor string to list of floats"""
    try:
        # Extract numbers from tensor string
        numbers = re.findall(r"[-+]?\d*\.\d+[eE]?[+-]?\d*", str(tensor_str))
        return [float(num) for num in numbers if num.strip()]
    except Exception as e:
        print(f"Embedding conversion error: {e}")
        return None

def main():
    print("🔄 Initializing ChromaDB...")
    
    # Initialize client and collection
    client = chromadb.PersistentClient(path="./chroma_videos_db")
    collection = client.get_or_create_collection(
        name="videos",
        metadata={"description": "Video transcripts with metadata and embeddings"}
    )
    
    print("✅ ChromaDB initialized")
    
    # Load data
    print("📂 Loading data...")
    df = pd.read_csv('final_embeddings.csv')
    videos_list = df.to_dict('records')
    
    print(f"🔢 Processing {len(videos_list)} videos...")
    
    ids = []
    documents = []
    embeddings = []
    metadatas = []
    
    successful_count = 0
    
    for i, video in enumerate(videos_list):
        try:
            # Handle NaN ID values
            vid_id = video.get('id')
            if pd.isna(vid_id):
                vid_id = str(uuid.uuid4())
            else:
                vid_id = str(vid_id)
            
            # Convert embedding
            embedding = convert_tensor_string(video['e_title_trans_tensor'])
            
            if embedding is None or len(embedding) == 0:
                print(f"⚠️  Skipping video {i} - embedding conversion failed")
                continue
            
            # Prepare data
            ids.append(vid_id)
            documents.append(str(video.get('transcript_cleaned', '')))
            embeddings.append(embedding)
            
            # Handle NaN values
            view_count = video.get('viewCount', 0)
            if pd.isna(view_count):
                view_count = 0
            
            # Prepare metadata
            metadata = {
                'title': str(video.get('title_cleaned', '')),
                'channel_title': str(video.get('channel_title', '')),
                'view_count': int(view_count),
                'duration': str(video.get('duration_seconds', '')),
                'video_id': vid_id
            }
            metadatas.append(metadata)
            successful_count += 1
            
            if successful_count % 100 == 0:
                print(f"✅ Processed {successful_count} videos...")
            
        except Exception as e:
            print(f"⚠️  Error processing video {i}: {e}")
            continue
    
    if successful_count > 0:
        # Add to collection
        print("💾 Saving to ChromaDB...")
        collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )
        
        print(f"✅ Successfully saved {successful_count} videos to vector DB")
        
        # Final verification
        final_count = collection.count()
        print(f"🎯 FINAL VERIFICATION:")
        print(f"   Collection count: {final_count}")
        print(f"   Collection name: videos")
        
        # Test retrieval
        test_results = collection.get(limit=2)
        print(f"   Test retrieval: {len(test_results['ids'])} items found")
        
    else:
        print("❌ No videos were saved due to errors")

if __name__ == "__main__":
    main()