import pandas as pd
import faiss
import numpy as np
import pickle
import os
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class FAISSVectorDB:
    def __init__(self, db_path="./faiss_videos_db"):
        self.db_path = db_path
        self.index_file = os.path.join(db_path, "faiss.index")
        self.metadata_file = os.path.join(db_path, "metadata.pkl")
        self.index = None
        self.metadata = []
        self.documents = []
        self.embedding_model = None
        
        self._load_index()
        self._load_embedding_model()
    
    def _load_index(self):
        """Load FAISS index and metadata"""
        try:
            if os.path.exists(self.index_file) and os.path.exists(self.metadata_file):
                self.index = faiss.read_index(self.index_file)
                with open(self.metadata_file, 'rb') as f:
                    data = pickle.load(f)
                    self.metadata = data.get('metadata', [])
                    self.documents = data.get('documents', [])
                print(f"✅ Loaded FAISS database with {len(self.metadata)} videos")
            else:
                print("❌ FAISS index not found. Please run vector.py first.")
                exit(1)
        except Exception as e:
            print(f"❌ Error loading FAISS index: {e}")
            exit(1)
    
    def _load_embedding_model(self):
        """Load SentenceTransformer model for semantic search"""
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            print("✅ Loaded SentenceTransformer model for semantic search")
        except Exception as e:
            print(f"❌ Error loading embedding model: {e}")
            print("❌ Semantic search requires sentence-transformers package")
            exit(1)
    
    def semantic_search(self, query, limit=10):
        """Semantic search using SentenceTransformer embeddings and cosine similarity"""
        try:
            # Generate query embedding
            print(f"🧠 Generating embeddings for query: '{query}'")
            query_embedding = self.embedding_model.encode([query])
            
            results = []
            
            print("🔍 Calculating semantic similarities...")
            for i, (doc, metadata) in enumerate(zip(self.documents, self.metadata)):
                # Generate document embedding
                doc_embedding = self.embedding_model.encode([doc])
                
                # Calculate cosine similarity
                similarity = cosine_similarity(query_embedding, doc_embedding)[0][0]
                
                # Check for keyword matches for additional context
                title = metadata.get('title', '').lower()
                transcript_lower = doc.lower()
                query_lower = query.lower()
                
                keyword_in_title = query_lower in title
                keyword_in_transcript = query_lower in transcript_lower
                
                results.append({
                    'id': metadata.get('original_id'),
                    'document': doc,
                    'metadata': metadata,
                    'similarity_score': float(similarity),
                    'keyword_in_title': keyword_in_title,
                    'keyword_in_transcript': keyword_in_transcript,
                    'title': metadata.get('title', ''),
                    'channel': metadata.get('channel_title', ''),
                    'views': metadata.get('view_count', 'N/A'),
                    'duration': metadata.get('duration', 'N/A')
                })
            
            # Sort by semantic similarity (highest first)
            results.sort(key=lambda x: x['similarity_score'], reverse=True)
            return results[:limit]
            
        except Exception as e:
            print(f"❌ Semantic search error: {e}")
            return []
    
    def get_document_by_id(self, doc_id):
        """Get document by ID"""
        for i, metadata in enumerate(self.metadata):
            if metadata.get('original_id') == doc_id:
                return {
                    'id': doc_id,
                    'document': self.documents[i],
                    'metadata': metadata
                }
        return None

def display_semantic_results(results, query):
    """Display semantic search results in a formatted way"""
    if not results:
        print(f"❌ No results found for '{query}'")
        return
    
    print(f"\n🎯 Found {len(results)} most relevant results for: '{query}'")
    print("=" * 120)
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. 📹 VIDEO RESULT")
        print(f"   🆔 ID: {result['id']}")
        print(f"   📺 Title: {result['title']}")
        print(f"   🏢 Channel: {result['channel']}")
        print(f"   👀 Views: {result['views']}")
        print(f"   ⏱️ Duration: {result['duration']}")
        print(f"   🧠 Semantic Similarity: {result['similarity_score']:.4f}")
        
        # Show keyword match indicators
        keyword_indicators = []
        if result['keyword_in_title']:
            keyword_indicators.append("✅ Keyword in Title")
        if result['keyword_in_transcript']:
            keyword_indicators.append("✅ Keyword in Transcript")
        
        if keyword_indicators:
            print(f"   🔍 {', '.join(keyword_indicators)}")
        
        # Show relevance interpretation
        similarity = result['similarity_score']
        if similarity >= 0.8:
            relevance = "🎯 Highly Relevant"
        elif similarity >= 0.6:
            relevance = "✅ Very Relevant"
        elif similarity >= 0.4:
            relevance = "⚠️  Moderately Relevant"
        elif similarity >= 0.2:
            relevance = "📝 Somewhat Relevant"
        else:
            relevance = "🔍 Low Relevance"
        
        print(f"   📊 Relevance: {relevance}")
        
        # Show most relevant snippet from transcript
        transcript = result['document']
        query_lower = query.lower()
        
        # Find the best matching segment
        sentences = transcript.split('.')
        best_sentence = ""
        best_score = 0
        
        for sentence in sentences:
            if len(sentence.strip()) > 20:  # Avoid very short sentences
                sentence_embedding = result['embedding_model'].encode([sentence])
                query_embedding = result['embedding_model'].encode([query])
                sentence_similarity = cosine_similarity(query_embedding, sentence_embedding)[0][0]
                
                if sentence_similarity > best_score:
                    best_score = sentence_similarity
                    best_sentence = sentence.strip()
        
        if best_sentence and len(best_sentence) > 0:
            # Truncate if too long
            if len(best_sentence) > 200:
                best_sentence = best_sentence[:200] + "..."
            print(f"   💡 Key Insight: {best_sentence}")
        else:
            # Fallback: show beginning of transcript
            preview = transcript[:150] + "..." if len(transcript) > 150 else transcript
            print(f"   📄 Preview: {preview}")
        
        print("-" * 120)

def main():
    """Main function - automatically uses semantic search"""
    print("🚀 Starting Semantic Video Search Engine")
    print("=" * 50)
    
    # Load database and model
    print("🔄 Initializing system...")
    faiss_db = FAISSVectorDB("./faiss_videos_db")
    
    if faiss_db.index is None or faiss_db.embedding_model is None:
        print("❌ Failed to initialize search engine")
        return
    
    print("✅ System ready for semantic search!")
    print("\n💡 Enter your search query and press Enter")
    print("   Example: 'machine learning tutorial', 'python programming', 'data science'")
    print("   Type 'exit' or 'quit' to stop\n")
    
    while True:
        print("\n" + "=" * 50)
        query = input("🔍 Enter your search query: ").strip()
        
        if query.lower() in ['exit', 'quit', 'q']:
            print("👋 Thank you for using Semantic Video Search!")
            break
        
        if not query:
            print("❌ Please enter a search query")
            continue
        
        # Ask for number of results
        limit_input = input("📊 Number of results to show (default 5): ").strip()
        try:
            limit = int(limit_input) if limit_input else 5
        except:
            limit = 5
            print("⚠️  Using default: 5 results")
        
        print(f"\n🧠 Searching for: '{query}'")
        print("⏳ Processing with AI semantic search...")
        
        # Perform semantic search
        results = faiss_db.semantic_search(query, limit=limit)
        
        # Display results
        display_semantic_results(results, query)
        
        # Show summary statistics
        if results:
            avg_similarity = sum(r['similarity_score'] for r in results) / len(results)
            max_similarity = max(r['similarity_score'] for r in results)
            min_similarity = min(r['similarity_score'] for r in results)
            
            print(f"\n📈 SEARCH SUMMARY:")
            print(f"   Average Similarity: {avg_similarity:.4f}")
            print(f"   Highest Similarity: {max_similarity:.4f}")
            print(f"   Lowest Similarity: {min_similarity:.4f}")
            
            # Count keyword matches
            title_matches = sum(1 for r in results if r['keyword_in_title'])
            transcript_matches = sum(1 for r in results if r['keyword_in_transcript'])
            print(f"   Keyword in Titles: {title_matches}/{len(results)}")
            print(f"   Keyword in Transcripts: {transcript_matches}/{len(results)}")
        
        # Ask if user wants to search again
        continue_search = input("\n🔍 Search again? (y/n): ").strip().lower()
        if continue_search not in ['y', 'yes', '']:
            print("👋 Thank you for using Semantic Video Search!")
            break

if __name__ == "__main__":
    main()