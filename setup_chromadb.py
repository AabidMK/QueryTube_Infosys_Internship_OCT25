import pandas as pd
import numpy as np
import ast
import chromadb
from chromadb.config import Settings
import json
import os

# Check if CSV file exists
csv_path = 'dataset_with_embeddings.csv'
if not os.path.exists(csv_path):
    print(f"Error: File '{csv_path}' not found!")
    print(f"Current directory: {os.getcwd()}")
    print("Make sure the CSV file is in the same directory as this script.")
    exit(1)

# Read the CSV file
print("Reading CSV file...")
df = pd.read_csv(csv_path)
print(f"Read {len(df)} rows from CSV")

# Prepare the data for ChromaDB
def prepare_chromadb_data(df):
    # Convert string embeddings to numpy arrays
    def parse_embedding(embedding_str):
        try:
            # Handle the string representation of the list
            if pd.isna(embedding_str):
                return []
            embedding_str = str(embedding_str).strip()
            if embedding_str.startswith('[') and embedding_str.endswith(']'):
                return ast.literal_eval(embedding_str)
        except Exception as e:
            print(f"Error parsing embedding: {e}")
            return []
        return []
    
    # Parse embeddings
    print("Parsing embeddings...")
    df['embeddings_parsed'] = df['embeddings'].apply(parse_embedding)
    
    # Filter out rows with empty embeddings or missing IDs
    initial_count = len(df)
    df = df[df['embeddings_parsed'].apply(lambda x: len(x) > 0)]
    df = df[df['id'].notna()]
    df['id'] = df['id'].astype(str)
    
    print(f"Filtered from {initial_count} to {len(df)} valid rows")
    
    # Check embedding dimensions
    embedding_lengths = df['embeddings_parsed'].apply(len)
    print(f"Embedding dimensions: min={embedding_lengths.min()}, max={embedding_lengths.max()}")
    
    # Prepare metadata
    metadata_list = []
    ids_list = []
    embeddings_list = []
    
    for _, row in df.iterrows():
        try:
            # Clean the ID
            video_id = str(row['id']).strip()
            if not video_id:
                continue
                
            metadata = {
                'title': str(row['title']) if pd.notnull(row['title']) else "Unknown",
                'channel_title': str(row['channel_title']) if pd.notnull(row['channel_title']) else "Unknown",
                'view_count': float(row['viewCount']) if pd.notnull(row['viewCount']) else 0.0,
                'duration': str(row['duration']) if pd.notnull(row['duration']) else "Unknown",
                'transcript': str(row['transcript'])[:1000] if pd.notnull(row['transcript']) else "",
                'published_at': str(row['publishedAt']) if pd.notnull(row['publishedAt']) else "",
                'tags': str(row['tags']) if pd.notnull(row['tags']) else "",
                'category_id': float(row['categoryId']) if pd.notnull(row['categoryId']) else 0.0
            }
            
            metadata_list.append(metadata)
            ids_list.append(video_id)
            embeddings_list.append(row['embeddings_parsed'])
            
        except Exception as e:
            print(f"Error processing row {row['id']}: {e}")
            continue
    
    print(f"Prepared {len(ids_list)} items for storage")
    return ids_list, embeddings_list, metadata_list

# Initialize ChromaDB
def initialize_chromadb(collection_name="youtube_videos"):
    # Create a persistent ChromaDB client
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    
    # Try to delete existing collection if it exists
    try:
        chroma_client.delete_collection(collection_name)
        print(f"Deleted existing collection: {collection_name}")
    except:
        print(f"No existing collection to delete or error deleting: {collection_name}")
    
    # Create new collection
    try:
        collection = chroma_client.create_collection(
            name=collection_name,
            metadata={"description": "YouTube videos with embeddings"}
        )
        print(f"Created new collection: {collection_name}")
        return collection
    except Exception as e:
        print(f"Error creating collection: {e}")
        # Try to get existing collection
        try:
            collection = chroma_client.get_collection(name=collection_name)
            print(f"Using existing collection: {collection_name}")
            return collection
        except:
            print(f"Failed to get collection: {collection_name}")
            raise

# Store data in ChromaDB
def store_in_chromadb(collection, ids, embeddings, metadatas):
    # Check if collection already has data
    existing_count = collection.count()
    if existing_count > 0:
        print(f"Collection already has {existing_count} items. Clearing...")
        # Get all existing IDs and delete them
        existing_data = collection.get()
        if existing_data['ids']:
            collection.delete(ids=existing_data['ids'])
    
    # Add documents to collection in batches to avoid memory issues
    batch_size = 100
    total_items = len(ids)
    
    for i in range(0, total_items, batch_size):
        end_idx = min(i + batch_size, total_items)
        batch_ids = ids[i:end_idx]
        batch_embeddings = embeddings[i:end_idx]
        batch_metadatas = metadatas[i:end_idx]
        
        try:
            collection.add(
                embeddings=batch_embeddings,
                metadatas=batch_metadatas,
                ids=batch_ids
            )
            print(f"Stored batch {i//batch_size + 1}: items {i+1}-{end_idx}")
        except Exception as e:
            print(f"Error storing batch {i//batch_size + 1}: {e}")
            # Try adding items one by one to identify the problematic one
            for j, (vid_id, emb, meta) in enumerate(zip(batch_ids, batch_embeddings, batch_metadatas)):
                try:
                    collection.add(
                        embeddings=[emb],
                        metadatas=[meta],
                        ids=[vid_id]
                    )
                except Exception as e2:
                    print(f"  Failed to add video {vid_id}: {e2}")
    
    print(f"\nTotal stored {total_items} documents in ChromaDB")

# Main execution
if __name__ == "__main__":
    print("Starting ChromaDB setup...")
    
    # Prepare data
    ids, embeddings, metadatas = prepare_chromadb_data(df)
    
    if len(ids) == 0:
        print("No valid data to store!")
        exit(1)
    
    # Initialize ChromaDB
    collection = initialize_chromadb()
    
    # Store data
    store_in_chromadb(collection, ids, embeddings, metadatas)
    
    # Verify the data was stored
    count = collection.count()
    print(f"\nCollection count: {count}")
    
    # Test query - find similar videos to the first one
    if len(embeddings) > 0:
        print("\nTesting query...")
        test_query = embeddings[0]
        results = collection.query(
            query_embeddings=[test_query],
            n_results=min(3, len(ids))
        )
        
        print("\nSample query results:")
        if results['ids'] and len(results['ids'][0]) > 0:
            for i, (vid_id, distance, metadata) in enumerate(zip(
                results['ids'][0], 
                results['distances'][0], 
                results['metadatas'][0]
            )):
                print(f"\nResult {i+1}:")
                print(f"ID: {vid_id}")
                print(f"Title: {metadata['title']}")
                print(f"Channel: {metadata['channel_title']}")
                print(f"Views: {metadata['view_count']}")
                print(f"Distance: {distance:.4f}")
        else:
            print("No results returned from query")
    
    print("\nSetup completed successfully!")
    print(f"Database saved to: {os.path.abspath('./chroma_db')}")