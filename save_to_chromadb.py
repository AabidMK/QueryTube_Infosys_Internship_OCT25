import pandas as pd
import chromadb
import ast
import numpy as np

def save_to_chromadb():
    try:
        # Read the CSV file
        print("Reading CSV file...")
        df = pd.read_csv('dataset_with_embeddings.csv')
        print(f"Found {len(df)} videos in the dataset")
        
        # Initialize ChromaDB client
        print("Initializing ChromaDB...")
        client = chromadb.PersistentClient(path="./chroma_db")
        
        # Create or get a collection
        collection = client.get_or_create_collection(
            name="youtube_videos",
            metadata={"description": "YouTube videos with embeddings"}
        )
        
        # Prepare data for ChromaDB
        documents = []
        metadatas = []
        ids = []
        embeddings = []
        
        print("Processing videos...")
        skipped_count = 0
        
        for i, row in df.iterrows():
            try:
                # Extract the required fields with validation
                video_id = str(row['id']).strip() if pd.notna(row['id']) else None
                
                # Skip if ID is missing or invalid
                if not video_id or video_id == 'nan' or video_id == 'None':
                    skipped_count += 1
                    continue
                
                transcript = str(row['transcript']) if pd.notna(row['transcript']) else ""
                title = str(row['title']) if pd.notna(row['title']) else "Unknown Title"
                channel_title = str(row['channel_title']) if pd.notna(row['channel_title']) else "Unknown Channel"
                view_count = float(row['viewCount']) if pd.notna(row['viewCount']) else 0.0
                duration = str(row['duration']) if pd.notna(row['duration']) else ""
                
                # Parse the embeddings string to list
                embedding_list = []
                if pd.notna(row['embeddings']):
                    try:
                        if isinstance(row['embeddings'], str):
                            embedding_list = ast.literal_eval(row['embeddings'])
                        else:
                            embedding_list = row['embeddings']
                    except:
                        try:
                            embedding_list = [float(x) for x in str(row['embeddings']).strip('[]').split(',')]
                        except:
                            print(f"Warning: Could not parse embeddings for video {video_id}")
                            skipped_count += 1
                            continue
                else:
                    print(f"Warning: Missing embeddings for video {video_id}")
                    skipped_count += 1
                    continue
                
                # Validate embedding list
                if not embedding_list or len(embedding_list) == 0:
                    print(f"Warning: Empty embeddings for video {video_id}")
                    skipped_count += 1
                    continue
                
                # Create document text (combining title and transcript for better search)
                document_text = f"Title: {title}. Content: {transcript}"
                
                # Append to lists
                documents.append(document_text)
                metadatas.append({
                    'video_id': video_id,
                    'title': title,
                    'channel_title': channel_title,
                    'view_count': view_count,
                    'duration': duration,
                    'transcript_preview': transcript[:300] + "..." if len(transcript) > 300 else transcript
                })
                ids.append(video_id)
                embeddings.append(embedding_list)
                
                if (i + 1) % 50 == 0:
                    print(f"Processed {i + 1} videos...")
                    
            except Exception as e:
                print(f"Error processing row {i}: {e}")
                skipped_count += 1
                continue
        
        print(f"Successfully processed {len(ids)} videos, skipped {skipped_count} videos")
        
        if len(ids) == 0:
            print("❌ No valid videos to add to ChromaDB")
            return
        
        # Add to ChromaDB collection
        print("Adding data to ChromaDB collection...")
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings
        )
        
        print(f"✅ Successfully stored {len(ids)} videos in ChromaDB")
        print(f"📊 Collection count: {collection.count()}")
        print(f"💾 Data persisted to: ./chroma_db/")
        print(f"🚫 Skipped {skipped_count} invalid entries")
        
        # Test the collection with a sample query
        print("\n🧪 Testing with a sample query...")
        try:
            results = collection.query(
                query_texts=["mystery science discovery"],
                n_results=3
            )
            
            print("Sample search results:")
            for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
                print(f"{i+1}. {metadata['title']} (Views: {metadata['view_count']})")
        except Exception as e:
            print(f"Query test failed: {e}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    save_to_chromadb()