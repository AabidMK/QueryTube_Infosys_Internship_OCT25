import pandas as pd
import faiss
import uuid
import numpy as np
import re
import pickle
import os
from datetime import datetime

def convert_tensor_string(tensor_str):
    """Convert tensor string to list of floats using NumPy"""
    try:
        # Handle different string formats that might contain embeddings
        if pd.isna(tensor_str) or tensor_str == '':
            return None
            
        tensor_str = str(tensor_str)
        
        # Case 1: String representation of numpy array
        if 'array(' in tensor_str and 'dtype=float' in tensor_str:
            # Extract the array content using regex
            array_match = re.search(r'array\(\[(.*?)\]', tensor_str, re.DOTALL)
            if array_match:
                array_content = array_match.group(1)
                # Clean and split the content
                numbers = re.findall(r"[-+]?\d*\.\d+[eE]?[+-]?\d*", array_content)
                return [float(num) for num in numbers if num.strip()]
        
        # Case 2: Simple list of numbers
        elif '[' in tensor_str and ']' in tensor_str:
            # Extract content between brackets
            list_match = re.search(r'\[(.*?)\]', tensor_str, re.DOTALL)
            if list_match:
                list_content = list_match.group(1)
                numbers = re.findall(r"[-+]?\d*\.\d+[eE]?[+-]?\d*", list_content)
                return [float(num) for num in numbers if num.strip()]
        
        # Case 3: Plain space/comma separated numbers
        else:
            numbers = re.findall(r"[-+]?\d*\.\d+[eE]?[+-]?\d*", tensor_str)
            if numbers:
                return [float(num) for num in numbers if num.strip()]
        
        print(f"⚠️  No numbers found in tensor string: {tensor_str[:100]}...")
        return None
        
    except Exception as e:
        print(f"Embedding conversion error: {e}")
        return None

def validate_embedding(embedding):
    """Validate embedding format and dimensions"""
    if embedding is None:
        return False
    if not isinstance(embedding, (list, np.ndarray)):
        return False
    if len(embedding) == 0:
        return False
    if not all(isinstance(x, (int, float, np.number)) for x in embedding):
        return False
    return True

class FAISSVectorDB:
    def __init__(self, db_path="./faiss_videos_db"):
        self.db_path = db_path
        self.index_file = os.path.join(db_path, "faiss.index")
        self.metadata_file = os.path.join(db_path, "metadata.pkl")
        self.index = None
        self.metadata = []
        self.documents = []
        
        os.makedirs(db_path, exist_ok=True)
        self._load_or_create_index()
    
    def _load_or_create_index(self):
        """Load existing FAISS index or create new one"""
        try:
            if os.path.exists(self.index_file) and os.path.exists(self.metadata_file):
                # Load existing index
                self.index = faiss.read_index(self.index_file)
                with open(self.metadata_file, 'rb') as f:
                    data = pickle.load(f)
                    self.metadata = data.get('metadata', [])
                    self.documents = data.get('documents', [])
                print(f"✅ Loaded existing FAISS index with {len(self.metadata)} items")
            else:
                print("✅ Creating new FAISS index")
                # We'll create the index when we know the dimension
        except Exception as e:
            print(f"❌ Error loading FAISS index: {e}")
    
    def _create_index(self, dimension):
        """Create FAISS index with given dimension"""
        self.index = faiss.IndexFlatIP(dimension)  # Inner product (cosine similarity)
        print(f"✅ Created FAISS index with dimension {dimension}")
    
    def save(self):
        """Save FAISS index and metadata"""
        try:
            if self.index is not None:
                faiss.write_index(self.index, self.index_file)
            
            with open(self.metadata_file, 'wb') as f:
                pickle.dump({
                    'metadata': self.metadata,
                    'documents': self.documents,
                    'total_count': len(self.metadata)
                }, f)
            
            print(f"💾 Saved FAISS index with {len(self.metadata)} items")
        except Exception as e:
            print(f"❌ Error saving FAISS index: {e}")
    
    def add(self, embeddings, documents, metadatas, ids):
        """Add items to FAISS index"""
        if len(embeddings) == 0:
            return
        
        # Convert to numpy array
        embeddings_array = np.array(embeddings, dtype=np.float32)
        
        # Create index if it doesn't exist
        if self.index is None:
            self._create_index(embeddings_array.shape[1])
        
        # Add to FAISS index
        self.index.add(embeddings_array)
        
        # Store metadata and documents
        for i, (doc, metadata, vid_id) in enumerate(zip(documents, metadatas, ids)):
            self.metadata.append({
                **metadata,
                'faiss_id': len(self.metadata),  # FAISS uses integer indices
                'original_id': vid_id,
                'document_index': len(self.documents)
            })
            self.documents.append(doc)
    
    def count(self):
        """Get total count of items"""
        if self.index is None:
            return 0
        return self.index.ntotal
    
    def get(self, limit=None):
        """Get items from FAISS index"""
        if limit is None:
            limit = self.count()
        
        results = {
            'ids': [m['original_id'] for m in self.metadata[:limit]],
            'documents': self.documents[:limit],
            'metadatas': self.metadata[:limit]
        }
        return results
    
    def query(self, query_embeddings, n_results=5):
        """Query FAISS index"""
        if self.index is None or self.index.ntotal == 0:
            return {'ids': [], 'distances': [], 'documents': [], 'metadatas': []}
        
        query_array = np.array(query_embeddings, dtype=np.float32)
        
        # Search in FAISS
        distances, indices = self.index.search(query_array, min(n_results, self.index.ntotal))
        
        results = {
            'ids': [],
            'distances': [],
            'documents': [],
            'metadatas': []
        }
        
        for i, (distance_list, index_list) in enumerate(zip(distances, indices)):
            batch_ids = []
            batch_distances = []
            batch_documents = []
            batch_metadatas = []
            
            for dist, idx in zip(distance_list, index_list):
                if idx < len(self.metadata):
                    batch_ids.append(self.metadata[idx]['original_id'])
                    batch_distances.append(float(dist))
                    batch_documents.append(self.documents[idx])
                    batch_metadatas.append(self.metadata[idx])
            
            results['ids'].append(batch_ids)
            results['distances'].append(batch_distances)
            results['documents'].append(batch_documents)
            results['metadatas'].append(batch_metadatas)
        
        return results

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
        'video_details': video_details
    }
    
    with open(output_file, 'wb') as f:
        pickle.dump(mapping, f)
    
    print(f"✅ Metadata mapping saved to {output_file}")
    return mapping

def main():
    print("📂 Loading data from CSV...")
    
    if not os.path.exists('final_embeddings.csv'):
        print("❌ Error: final_embeddings.csv not found in current directory")
        print("📁 Current directory files:")
        for file in os.listdir('.'):
            print(f"   - {file}")
        return
    
    df = pd.read_csv('final_embeddings.csv')
    
    print("🔄 Initializing FAISS VectorDB...")
    
    # Initialize FAISS database
    faiss_db = FAISSVectorDB("./faiss_videos_db")
    
    print("✅ FAISS VectorDB initialized")
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
            
            if not validate_embedding(embedding):
                print(f"⚠️  Skipping video {i} - embedding conversion failed or invalid")
                failed_conversions += 1
                
                video_detail = {
                    'faiss_id': 'FAILED',
                    'original_id': original_id if not pd.isna(original_id) else 'unknown',
                    'title': video.get('title_cleaned', ''),
                    'channel': video.get('channel_title', ''),
                    'embedding_success': False,
                    'dataframe_index': i,
                    'error': 'Embedding conversion failed'
                }
                video_details.append(video_detail)
                continue
            
            # Convert to numpy array for validation
            embedding_array = np.array(embedding, dtype=np.float32)
            
            # Check for NaN or Inf values
            if np.any(np.isnan(embedding_array)) or np.any(np.isinf(embedding_array)):
                print(f"⚠️  Skipping video {i} - embedding contains NaN or Inf values")
                failed_conversions += 1
                continue
            
            # Track embedding dimensions
            embedding_dimensions.add(len(embedding_array))
            
            # Prepare data for FAISS
            ids.append(vid_id)
            documents.append(str(video.get('transcript_cleaned', '')))
            embeddings.append(embedding_array.tolist())
            
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
                'video_id': vid_id,
                'original_id': str(original_id) if not generated_id else 'generated',
                'embedding_dimension': len(embedding_array)
            }
            metadatas.append(metadata)
            
            # Store detailed mapping
            video_detail = {
                'faiss_id': vid_id,
                'original_id': original_id if not pd.isna(original_id) else 'generated',
                'title': video.get('title_cleaned', ''),
                'channel': video.get('channel_title', ''),
                'view_count': int(view_count),
                'embedding_success': True,
                'embedding_dimension': len(embedding_array),
                'dataframe_index': i,
                'embedding_norm': float(np.linalg.norm(embedding_array))
            }
            video_details.append(video_detail)
            
            successful_count += 1
            
            if successful_count % 100 == 0:
                print(f"✅ Processed {successful_count} videos...")
            
        except Exception as e:
            print(f"⚠️  Error processing video {i}: {e}")
            failed_conversions += 1
            
            video_detail = {
                'faiss_id': 'FAILED',
                'original_id': original_id if 'original_id' in locals() and not pd.isna(original_id) else 'unknown',
                'title': video.get('title_cleaned', '') if 'video' in locals() else '',
                'channel': video.get('channel_title', '') if 'video' in locals() else '',
                'embedding_success': False,
                'dataframe_index': i,
                'error': str(e)
            }
            video_details.append(video_detail)
            continue
    
    # Create metadata mapping pickle file
    print("💾 Creating metadata mapping pickle file...")
    mapping = create_and_save_metadata_mapping(
        video_details, successful_count, failed_conversions, 
        embedding_dimensions, df, "metadata_mapping.pkl"
    )
    
    if successful_count > 0:
        # Add to FAISS database
        print("💾 Saving to FAISS VectorDB...")
        try:
            faiss_db.add(embeddings, documents, metadatas, ids)
            faiss_db.save()
            
            print(f"✅ Successfully saved {successful_count} videos to FAISS VectorDB")
            
            # Final verification
            final_count = faiss_db.count()
            print(f"🎯 FINAL VERIFICATION:")
            print(f"   FAISS count: {final_count}")
            print(f"   Successful embeddings: {successful_count}")
            print(f"   Failed conversions: {failed_conversions}")
            print(f"   Embedding dimensions: {embedding_dimensions}")
            print(f"   Metadata mapping: metadata_mapping.pkl")
            
            # Test retrieval
            test_results = faiss_db.get(limit=2)
            print(f"   Test retrieval: {len(test_results['ids'])} items found")
            
            # Test similarity search
            if len(embeddings) > 0:
                test_embedding = embeddings[0]
                similar_results = faiss_db.query(
                    query_embeddings=[test_embedding],
                    n_results=1
                )
                print(f"   Similarity search test: {len(similar_results['ids'][0])} result(s) found")
            
        except Exception as e:
            print(f"❌ Error saving to FAISS: {e}")
            print("✅ But metadata mapping was still saved to pickle file!")
        
    else:
        print("❌ No videos were saved to FAISS due to errors")
        print("✅ But metadata mapping was still saved to pickle file!")
    
    # Final confirmation
    if os.path.exists("metadata_mapping.pkl"):
        print(f"\n🎉 METADATA PICKLE FILE CREATED SUCCESSFULLY!")
        print(f"   File: metadata_mapping.pkl")
        print(f"   Size: {os.path.getsize('metadata_mapping.pkl')} bytes")
        
        with open("metadata_mapping.pkl", 'rb') as f:
            metadata = pickle.load(f)
        print(f"   Contains: {len(metadata['video_details'])} video mappings")
        print(f"   Successful: {metadata['successful_embeddings']}")
        print(f"   Failed: {metadata['failed_embeddings']}")
    else:
        print("❌ ERROR: Pickle file was not created!")

if __name__ == "__main__":
    main()