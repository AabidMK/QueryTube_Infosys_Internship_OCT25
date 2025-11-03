import pickle
import pandas as pd

# Load and display the metadata mapping
with open('metadata_mapping.pkl', 'rb') as f:
    metadata = pickle.load(f)

print("🎯 METADATA MAPPING CONTENTS:")
print(f"📊 Summary:")
print(f"   - Total videos processed: {metadata['total_videos_processed']}")
print(f"   - Successful embeddings: {metadata['successful_embeddings']}")
print(f"   - Failed embeddings: {metadata['failed_embeddings']}")
print(f"   - Embedding dimensions: {metadata['embedding_dimensions']}")
print(f"   - Timestamp: {metadata['ingestion_timestamp']}")

print(f"\n📋 Sample video mappings (first 5):")
for i, video in enumerate(metadata['video_details'][:5]):
    print(f"   {i+1}. ID: {video['chromadb_id']}")
    print(f"      Title: {video['title'][:50]}...")
    print(f"      Channel: {video['channel']}")
    print(f"      Success: {video['embedding_success']}")
    print(f"      DataFrame Index: {video['dataframe_index']}")
    print()

print(f"🔍 Total video mappings stored: {len(metadata['video_details'])}")