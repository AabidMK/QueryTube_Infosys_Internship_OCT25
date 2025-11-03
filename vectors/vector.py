import pandas as pd
import chromadb
import uuid
import numpy as np
import re
import pickle
import os
from datetime import datetime

def convert_tensor_string(tensor_str):
    """Convert tensor string to list of floats"""
    try:
        # Extract numbers from tensor string
        numbers = re.findall(r"[-+]?\d*\.\d+[eE]?[+-]?\d*", str(tensor_str))
        return [float(num) for num in numbers if num.strip()]
    except Exception as e:
        print(f"Embedding conversion error: {e}")
        return None

def create_and_save_metadata_mapping(video_details, successful_count, failed_count, embedding_dimensions, df, output_file="metadata_mapping.pkl"):
    """Create comprehensive metadata mapping and save to pickle"""
    mapping = {
        'ingestion_timestamp': datetime.now().isoformat(),
        'total_videos_processed': len(df),
        'successful_embeddings': successful_count,
        'failed_embeddings': failed_count,
        'embedding_source': 'e_title_trans_tensor',
        'embedding_dimensions': list(embedding_dimensions),
        'dataframe_columns': list(df.columns),
        'dataframe_shape': df.shape,
        'video_details': video_details  # Add individual video details
    }
    
    # Save to pickle
    with open(output_file, 'wb') as f:
        pickle.dump(mapping, f)
    
    print(f"✅ Metadata mapping saved to {output_file}")
    return mapping

def main():
    print("📂 Loading data from CSV...")
    
    # Make sure the CSV file exists in the current directory
    if not os.path.exists('final_embeddings.csv'):
        print("❌ Error: final_embeddings.csv not found in current directory")
        print("📁 Current directory files:")
        for file in os.listdir('.'):
            print(f"   - {file}")
        return
    
    df = pd.read_csv('final_embeddings.csv')
    
    print("🔄 Initializing ChromaDB...")
    
    # Initialize client and collection
    client = chromadb.PersistentClient(path="./chroma_videos_db")
    collection = client.get_or_create_collection(
        name="videos",
        metadata={"description": "Video transcripts with metadata and embeddings"}
    )
    
    print("✅ ChromaDB initialized")
    print(f"📊 Processing DataFrame with {len(df)} videos...")
    
    ids = []
    documents = []
    embeddings = []
    metadatas = []
    
    successful_count = 0
    failed_conversions = 0
    embedding_dimensions = set()
    video_details = []
    
    for i, video in enumerate(df.to_dict('records')):
        try:
            # Handle NaN ID values
            vid_id = video.get('id')
            original_id = vid_id
            if pd.isna(vid_id):
                vid_id = str(uuid.uuid4())
                generated_id = True
            else:
                vid_id = str(vid_id)
                generated_id = False
            
            # Convert embedding
            embedding = convert_tensor_string(video.get('e_title_trans_tensor', ''))
            
            if embedding is None or len(embedding) == 0:
                print(f"⚠️  Skipping video {i} - embedding conversion failed")
                failed_conversions += 1
                
                # Still record failed videos in metadata
                video_detail = {
                    'chromadb_id': 'FAILED',
                    'original_id': original_id if not pd.isna(original_id) else 'unknown',
                    'title': video.get('title_cleaned', ''),
                    'channel': video.get('channel_title', ''),
                    'embedding_success': False,
                    'dataframe_index': i,
                    'error': 'Embedding conversion failed'
                }
                video_details.append(video_detail)
                continue
            
            # Track embedding dimensions
            embedding_dimensions.add(len(embedding))
            
            # Prepare data for ChromaDB
            ids.append(vid_id)
            documents.append(str(video.get('transcript_cleaned', '')))
            embeddings.append(embedding)
            
            # Handle NaN values
            view_count = video.get('viewCount', 0)
            if pd.isna(view_count):
                view_count = 0
            
            # Prepare metadata for ChromaDB
            metadata = {
                'title': str(video.get('title_cleaned', '')),
                'channel_title': str(video.get('channel_title', '')),
                'view_count': int(view_count),
                'duration': str(video.get('duration_seconds', '')),
                'video_id': vid_id,
                'original_id': str(original_id) if not generated_id else 'generated',
                'embedding_dimension': len(embedding)
            }
            metadatas.append(metadata)
            
            # Store detailed mapping for pickle
            video_detail = {
                'chromadb_id': vid_id,
                'original_id': original_id if not pd.isna(original_id) else 'generated',
                'title': video.get('title_cleaned', ''),
                'channel': video.get('channel_title', ''),
                'view_count': int(view_count),
                'embedding_success': True,
                'embedding_dimension': len(embedding),
                'dataframe_index': i
            }
            video_details.append(video_detail)
            
            successful_count += 1
            
            if successful_count % 100 == 0:
                print(f"✅ Processed {successful_count} videos...")
            
        except Exception as e:
            print(f"⚠️  Error processing video {i}: {e}")
            failed_conversions += 1
            continue
    
    # ✅ CREATE PICKLE FILE FIRST (before ChromaDB operations)
    print("💾 Creating metadata mapping pickle file...")
    mapping = create_and_save_metadata_mapping(
        video_details, successful_count, failed_conversions, 
        embedding_dimensions, df, "metadata_mapping.pkl"
    )
    
    if successful_count > 0:
        # Add to ChromaDB collection
        print("💾 Saving to ChromaDB...")
        try:
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
            print(f"   Successful embeddings: {successful_count}")
            print(f"   Failed conversions: {failed_conversions}")
            print(f"   Embedding dimensions: {embedding_dimensions}")
            print(f"   Metadata mapping: metadata_mapping.pkl")
            
            # Test retrieval
            test_results = collection.get(limit=2)
            print(f"   Test retrieval: {len(test_results['ids'])} items found")
            
        except Exception as e:
            print(f"❌ Error saving to ChromaDB: {e}")
            print("✅ But metadata mapping was still saved to pickle file!")
        
    else:
        print("❌ No videos were saved to ChromaDB due to errors")
        print("✅ But metadata mapping was still saved to pickle file!")
    
    # Final confirmation
    if os.path.exists("metadata_mapping.pkl"):
        print(f"\n🎉 METADATA PICKLE FILE CREATED SUCCESSFULLY!")
        print(f"   File: metadata_mapping.pkl")
        print(f"   Size: {os.path.getsize('metadata_mapping.pkl')} bytes")
        
        # Show quick summary
        with open("metadata_mapping.pkl", 'rb') as f:
            metadata = pickle.load(f)
        print(f"   Contains: {len(metadata['video_details'])} video mappings")
    else:
        print("❌ ERROR: Pickle file was not created!")

if __name__ == "__main__":
    main()