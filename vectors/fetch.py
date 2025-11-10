import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import ast
import re

class VideoSearchEngine:
    def __init__(self, pickle_file: str = "metadata_mapping.pkl", csv_file: str = "final_embeddings.csv"):
        """Initialize the video search engine with optimized caching"""
        self.model = None
        self.embeddings_cache = None
        self.metadata_cache = None
        
        # Load components
        self._load_embedding_model()
        self._load_and_cache_data(pickle_file, csv_file)
    
    def _load_embedding_model(self):
        """Load the embedding model"""
        try:
            self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            print("✅ Embedding model loaded")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
    
    def _load_and_cache_data(self, pickle_file: str, csv_file: str):
        """Load and cache embeddings and metadata"""
        try:
            # Load metadata
            with open(pickle_file, 'rb') as f:
                metadata_mapping = pickle.load(f)
            
            # Load CSV data
            df = pd.read_csv(csv_file)
            
            # Create metadata lookup
            video_details = metadata_mapping.get('video_details', [])
            metadata_map = {vd.get('original_id'): vd for vd in video_details if vd.get('original_id')}
            
            # Parse embeddings
            embedding_column = metadata_mapping.get('embedding_source', 'e_title_trans_tensor')
            embeddings_list = []
            metadata_list = []
            
            for _, row in df.iterrows():
                video_id = row.get('id')
                if not video_id or video_id not in metadata_map:
                    continue
                
                embedding_str = row.get(embedding_column, '')
                if pd.isna(embedding_str) or not embedding_str:
                    continue
                
                embedding = self._parse_embedding(embedding_str)
                if embedding is not None:
                    embeddings_list.append(embedding)
                    metadata = metadata_map[video_id]
                    # Ensure title is a string
                    title = metadata.get('title', '')
                    if not isinstance(title, str):
                        title = str(title) if not pd.isna(title) else ''
                    
                    metadata_list.append({
                        'video_id': video_id,
                        'title': title,
                        'channel_title': metadata.get('channel', ''),
                        'view_count': metadata.get('view_count', 0)
                    })
            
            if embeddings_list:
                self.embeddings_cache = np.array(embeddings_list)
                self.metadata_cache = metadata_list
                print(f"✅ Cached {len(embeddings_list)} embeddings")
            else:
                print("❌ No embeddings loaded")
                
        except Exception as e:
            print(f"❌ Error loading data: {e}")
    
    def _parse_embedding(self, tensor_str: str):
        """Parse embedding string to numpy array"""
        if not tensor_str or pd.isna(tensor_str):
            return None
        
        tensor_str = str(tensor_str).strip()
        
        # Handle tensor([...]) format
        if tensor_str.startswith('tensor(') and tensor_str.endswith(')'):
            try:
                content = tensor_str[7:-1].strip()
                if content.startswith('[') and content.endswith(']'):
                    content = content[1:-1]
                numbers = [float(x) for x in content.split(',')]
                if len(numbers) == 384:
                    return np.array(numbers, dtype=np.float32)
            except (ValueError, AttributeError):
                pass
        
        # Handle list format
        elif tensor_str.startswith('[') and tensor_str.endswith(']'):
            try:
                parsed = ast.literal_eval(tensor_str)
                if isinstance(parsed, list) and len(parsed) == 384:
                    return np.array(parsed, dtype=np.float32)
            except (ValueError, SyntaxError):
                pass
        
        return None
    
    def _expand_query(self, query: str) -> str:
        """Expand query with synonyms and related terms"""
        # Add context words to make query more descriptive
        query_lower = query.lower()
        
        # Common expansions for video search
        expansions = {
            'tutorial': 'tutorial guide how to learn',
            'review': 'review opinion analysis',
            'vlog': 'vlog daily life video blog',
            'gaming': 'gaming gameplay video game',
            'music': 'music song audio',
            'cooking': 'cooking recipe food',
            'fitness': 'fitness workout exercise training',
            'travel': 'travel adventure journey trip',
            'tech': 'technology tech gadget',
            'news': 'news latest update',
        }
        
        # Check if query contains any expansion triggers
        for key, expansion in expansions.items():
            if key in query_lower and len(query.split()) <= 2:
                return expansion
        
        return query
    
    def _get_query_embedding(self, query: str):
        """Convert query to embedding with query expansion"""
        if self.model is None:
            return None
        try:
            # Expand query for better matching
            expanded_query = self._expand_query(query)
            return self.model.encode(expanded_query, convert_to_tensor=False).astype(np.float32)
        except Exception as e:
            print(f"❌ Error generating embedding: {e}")
            return None
    
    def _calculate_keyword_boost(self, query: str, title: str) -> float:
        """Calculate keyword matching boost"""
        # Handle non-string titles
        if not isinstance(title, str) or not title:
            return 0.0
        
        try:
            query_words = set(re.findall(r'\w+', query.lower()))
            title_words = set(re.findall(r'\w+', title.lower()))
            
            if not query_words:
                return 0.0
            
            # Calculate word overlap with higher boost
            overlap = len(query_words & title_words)
            
            # Progressive boost: more matches = higher boost
            if overlap == len(query_words):
                # All query words found - give maximum boost
                boost = 0.30
            elif overlap > 0:
                # Partial match - scale boost
                boost = (overlap / len(query_words)) * 0.25
            else:
                boost = 0.0
            
            return boost
        except Exception:
            return 0.0
    
    def search(self, query: str, top_k: int = 5, use_boost: bool = True):
        """Search for similar videos with enhanced scoring"""
        if self.embeddings_cache is None or self.metadata_cache is None:
            print("❌ Search engine not initialized")
            return []
        
        query_embedding = self._get_query_embedding(query)
        if query_embedding is None:
            return []
        
        # Calculate base similarities
        similarities = cosine_similarity([query_embedding], self.embeddings_cache)[0]
        
        # Apply keyword boost if enabled
        if use_boost:
            for idx, metadata in enumerate(self.metadata_cache):
                keyword_boost = self._calculate_keyword_boost(query, metadata['title'])
                similarities[idx] = min(1.0, similarities[idx] + keyword_boost)
        
        # Get top K results
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            metadata = self.metadata_cache[idx]
            results.append({
                'video_id': metadata['video_id'],
                'title': metadata['title'],
                'channel_title': metadata['channel_title'],
                'similarity_score': float(similarities[idx]),
                'view_count': metadata['view_count']
            })
        
        return results
    
    def display_results(self, results: list, query: str):
        """Display search results"""
        if not results:
            print(f"❌ No results found for: '{query}'")
            return
        
        print(f"\n🎬 TOP {len(results)} VIDEOS FOR: '{query}'")
        print("=" * 60)
        
        for i, video in enumerate(results, 1):
            print(f"\n🏆 Rank #{i} (Score: {video['similarity_score']:.1%})")
            print(f"   📺 {video['title']}")
            print(f"   👨‍💼 {video['channel_title']}")
            print(f"   🆔 {video['video_id']}")
            print(f"   👀 {video['view_count']} views")

def main():
    """Main function to run the search engine"""
    print("🚀 Initializing Enhanced Video Search Engine...")
    search_engine = VideoSearchEngine()
    
    while True:
        print("\n" + "="*50)
        print("🎥 VIDEO SEARCH ENGINE (Enhanced Scoring)")
        print("="*50)
        
        query = input("\n🔍 Enter search query (or 'quit' to exit): ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        
        if not query:
            print("❌ Please enter a query")
            continue
        
        # Perform search with enhanced scoring
        results = search_engine.search(query, top_k=5, use_boost=True)
        search_engine.display_results(results, query)

if __name__ == "__main__":
    main()