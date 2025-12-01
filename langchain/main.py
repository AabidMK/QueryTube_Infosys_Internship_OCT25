# youtube_search.py
"""
YouTube Video Search Engine using LangChain
Single File Solution - Everything in one file
"""

import os
import sys
import pandas as pd
import numpy as np
import pickle
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional
from config import Config

# LangChain imports
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

class YouTubeSearchEngine:
    """Complete YouTube search engine in one class"""
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        self.embedding_model = Config.EMBEDDING_MODEL
        self.gemini_model = Config.GEMINI_MODEL
        self.default_top_k = Config.DEFAULT_TOP_K
        self.vector_store_path = str(Config.VECTOR_STORE_PATH)
        
        # Initialize components
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.embedding_model,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        self.vector_store = None
        self.metadata_mapping = {}
        
        # Initialize Gemini for summaries
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        self.llm = None
        self.summary_chain = None
        
        if self.gemini_api_key:
            self._init_gemini()
    
    def _init_gemini(self):
        """Initialize Gemini for AI summaries"""
        try:
            self.llm = ChatGoogleGenerativeAI(
                model=self.gemini_model,
                google_api_key=self.gemini_api_key,
                temperature=0.1,
                max_tokens=300
            )
            
            # Create summary prompt
            summary_prompt = ChatPromptTemplate.from_template("""
            Create a concise, engaging summary of this YouTube video (80-120 words):
            
            Title: {title}
            Content: {content}
            
            Focus on the main topics, key takeaways, and who would benefit from watching.
            Make it engaging and informative.
            
            Summary:
            """)
            
            self.summary_chain = summary_prompt | self.llm | StrOutputParser()
            
        except Exception as e:
            print(f"⚠️  Gemini initialization failed: {e}")
            print("AI summaries will not be available.")
    
    def load_or_create_index(self, csv_path: Optional[str] = None, force_create: bool = False):
        """Load existing index or create new one from CSV"""
    
        # Use config DATASET_PATH if csv_path not provided
        if csv_path is None:
            csv_path = str(Config.DATASET_PATH)
    
        # Check if index exists
        if not force_create and Path(self.vector_store_path).exists() and Path(f"{self.vector_store_path}/index.faiss").exists():
            print(f"📂 Loading existing index from: {self.vector_store_path}")
            self._load_existing_index()
            return True
        else:
            print(f"📁 Creating new index from: {csv_path}")
            return self._create_index_from_csv(csv_path)
    
    def _create_index_from_csv(self, csv_path: str) -> bool:
        """Create FAISS index from CSV file"""
        try:
            # Load dataset
            print("Loading dataset...")
            df = pd.read_csv(csv_path)
            print(f"📊 Dataset loaded: {len(df)} rows, {len(df.columns)} columns")
            
            # Create documents
            print("Creating documents...")
            documents = []
            
            for idx, row in df.iterrows():
                # Create document content
                content_parts = []
                
                if 'title' in df.columns and pd.notna(row.get('title')):
                    content_parts.append(f"Title: {row['title']}")
                
                if 'description' in df.columns and pd.notna(row.get('description')):
                    desc = str(row['description'])[:300]  # Limit description
                    content_parts.append(f"Description: {desc}")
                
                if 'transcript' in df.columns and pd.notna(row.get('transcript')):
                    transcript = str(row['transcript'])[:500]  # Limit transcript
                    content_parts.append(f"Transcript: {transcript}")
                
                content = "\n".join(content_parts)
                
                # Create metadata
                metadata = {
                    'row_id': str(idx),
                    'video_id': str(row.get('video_id', idx)) if 'video_id' in df.columns else str(idx),
                    'title': str(row.get('title', '')) if 'title' in df.columns else 'No Title',
                }
                
                # Add other fields
                for field in ['channel', 'views', 'likes', 'duration', 'published_date']:
                    if field in df.columns and pd.notna(row.get(field)):
                        metadata[field] = str(row[field])
                
                # Store full row data
                self.metadata_mapping[str(idx)] = row.to_dict()
                
                # Create document
                doc = Document(page_content=content, metadata=metadata)
                documents.append(doc)
                
                # Progress indicator
                if idx % 1000 == 0 and idx > 0:
                    print(f"  Processed {idx} documents...")
            
            print(f"✅ Created {len(documents)} documents")
            
            # Create FAISS index
            print("Building FAISS vector store...")
            self.vector_store = FAISS.from_documents(documents, self.embeddings)
            
            # Save index
            self._save_index()
            
            print(f"✅ Index created and saved to: {self.vector_store_path}")
            print(f"   Total vectors: {self.vector_store.index.ntotal}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating index: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _save_index(self):
        """Save FAISS index and metadata"""
        if self.vector_store:
            # Create directory if it doesn't exist
            Path(self.vector_store_path).mkdir(parents=True, exist_ok=True)
        
            # Save FAISS index
            self.vector_store.save_local(self.vector_store_path)
        
            # Save metadata - use Config.METADATA_PATH
            metadata_path = Config.METADATA_PATH
            with open(metadata_path, 'wb') as f:
                pickle.dump(self.metadata_mapping, f)
        
            print(f"💾 Index saved to {self.vector_store_path}")
    
    def _load_existing_index(self):
        """Load existing FAISS index"""
        try:
            # Load FAISS index
            self.vector_store = FAISS.load_local(
                folder_path=self.vector_store_path,
                embeddings=self.embeddings,
                allow_dangerous_deserialization=True
            )
            
            # Load metadata
            metadata_path = os.path.join(self.vector_store_path, "metadata.pkl")
            if os.path.exists(metadata_path):
                with open(metadata_path, 'rb') as f:
                    self.metadata_mapping = pickle.load(f)
            
            print(f"✅ Loaded index with {self.vector_store.index.ntotal} vectors")
            return True
            
        except Exception as e:
            print(f"❌ Error loading index: {e}")
            return False
    
    def search(self, query: str, top_k: int = 5, include_summary: bool = True) -> Dict[str, Any]:
        """Search for videos"""
        if not self.vector_store:
            raise ValueError("Vector store not loaded. Call load_or_create_index() first.")
        
        print(f"🔍 Searching for: '{query}'")
        
        # Perform similarity search with scores
        results_with_scores = self.vector_store.similarity_search_with_score(query, k=top_k)
        
        # Process results
        videos = []
        for i, (doc, score) in enumerate(results_with_scores):
            video_result = self._process_result(doc, score, i+1)
            
            # Generate AI summary if requested
            if include_summary and self.summary_chain:
                video_result['ai_summary'] = self._generate_ai_summary(video_result)
            
            videos.append(video_result)
        
        return {
            'query': query,
            'total_results': len(videos),
            'videos': videos
        }
    
    def _process_result(self, doc: Document, score: float, rank: int) -> Dict[str, Any]:
        """Process a single search result"""
        row_id = doc.metadata.get('row_id', '')
        full_data = self.metadata_mapping.get(row_id, {})
        
        # Convert distance to similarity score (0-1)
        similarity = 1 / (1 + score) if score > 0 else 1.0
        
        # Build result
        result = {
            'rank': rank,
            'similarity_score': round(similarity, 4),
            'distance_score': round(float(score), 4),
            'title': doc.metadata.get('title', 'Unknown'),
            'video_id': doc.metadata.get('video_id', 'N/A'),
        }
        
        # Add available metadata
        for field in ['channel', 'views', 'likes', 'duration', 'published_date']:
            if field in doc.metadata:
                result[field] = doc.metadata[field]
        
        # Add transcript if available
        if 'transcript' in full_data:
            transcript = str(full_data['transcript'])
            result['transcript_excerpt'] = transcript[:500] + "..." if len(transcript) > 500 else transcript
            result['has_transcript'] = True
        else:
            result['has_transcript'] = False
        
        # Store full data reference
        result['_full_data_ref'] = row_id
        
        return result
    
    def _generate_ai_summary(self, video_data: Dict[str, Any]) -> str:
        """Generate AI summary using Gemini"""
        if not self.summary_chain:
            return "AI summary not available (Gemini not initialized)"
        
        try:
            # Get content for summary
            content = video_data.get('transcript_excerpt', '')
            if not content:
                content = video_data.get('title', '')
            
            # Generate summary
            summary = self.summary_chain.invoke({
                'title': video_data.get('title', 'YouTube Video'),
                'content': content
            })
            
            return summary.strip()
            
        except Exception as e:
            return f"Failed to generate summary: {str(e)}"
    
    def print_results(self, results: Dict[str, Any], output_format: str = 'text'):
        """Print results in specified format"""
        if output_format == 'json':
            print(json.dumps(results, indent=2, ensure_ascii=False))
            return
        
        # Text format
        print("\n" + "="*80)
        print(f"SEARCH RESULTS")
        print(f"Query: {results['query']}")
        print(f"Found: {results['total_results']} videos")
        print("="*80)
        
        for video in results['videos']:
            print(f"\n#{video['rank']}: {video['title']}")
            print(f"   Score: {video['similarity_score']:.3f} (Distance: {video['distance_score']:.4f})")
            print(f"   ID: {video.get('video_id', 'N/A')}")
            
            if 'channel' in video:
                print(f"   📺 Channel: {video['channel']}")
            
            if 'views' in video:
                print(f"   👁️ Views: {video['views']}")
            
            if 'duration' in video:
                print(f"   ⏱️ Duration: {video['duration']}")
            
            if 'ai_summary' in video:
                print(f"\n   🤖 AI SUMMARY:")
                # Split summary into lines for better formatting
                summary_lines = video['ai_summary'].split('. ')
                for line in summary_lines:
                    if line.strip():
                        print(f"      {line.strip()}.")
            
            print("-" * 80)
    
    def interactive_search(self):
        """Run interactive search session"""
        print("\n" + "="*60)
        print("YOUTUBE VIDEO SEARCH ENGINE")
        print("="*60)
        
        # Check if index exists
        if not self.vector_store:
            print("\n⚠️  No index loaded. You need to create one first.")
            csv_path = input("Enter path to your CSV dataset: ").strip()
            if not csv_path:
                csv_path = "../master_dataset_embedded.csv"
            
            if not os.path.exists(csv_path):
                print(f"❌ File not found: {csv_path}")
                return
            
            self.load_or_create_index(csv_path, force_create=True)
        
        # Interactive loop
        while True:
            print("\n" + "-"*60)
            query = input("\nEnter search query (or 'quit' to exit): ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not query:
                continue
            
            try:
                top_k = input("Number of results (default 5): ").strip()
                top_k = int(top_k) if top_k.isdigit() else 5
                
                include_summary_input = input("Include AI summaries? (y/n, default y): ").strip().lower()
                include_summary = include_summary_input != 'n'
                
                # Perform search
                results = self.search(query, top_k, include_summary)
                
                # Ask for output format
                format_input = input("Output format (text/json, default text): ").strip().lower()
                output_format = 'json' if format_input == 'json' else 'text'
                
                # Print results
                self.print_results(results, output_format)
                
                # Ask to save results
                save_input = input("\nSave results to file? (y/n): ").strip().lower()
                if save_input == 'y':
                    filename = input("Filename (default: results.json): ").strip()
                    filename = filename if filename else "results.json"
                    
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(results, f, indent=2, ensure_ascii=False)
                    print(f"✅ Results saved to {filename}")
                
            except Exception as e:
                print(f"❌ Error during search: {e}")


def main():
    """Main function - handles command line arguments"""
    parser = argparse.ArgumentParser(
        description='YouTube Video Search Engine using LangChain',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--query', '-q',
        type=str,
        help='Search query'
    )
    
    parser.add_argument(
        '--csv',
        type=str,
        default='../master_dataset_embedded.csv',
        help='Path to CSV dataset (for creating index)'
    )
    
    parser.add_argument(
        '--create-index',
        action='store_true',
        help='Create new vector index (overwrites existing)'
    )
    
    parser.add_argument(
        '--top-k', '-k',
        type=int,
        default=5,
        help='Number of results to return'
    )
    
    parser.add_argument(
        '--no-summary',
        action='store_true',
        help='Disable AI summaries'
    )
    
    parser.add_argument(
        '--output', '-o',
        choices=['text', 'json'],
        default='text',
        help='Output format'
    )
    
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Run in interactive mode'
    )
    
    parser.add_argument(
        '--api-key',
        type=str,
        help='Gemini API key (or set GEMINI_API_KEY in .env)'
    )
    
    args = parser.parse_args()
    
    # Initialize search engine
    search_engine = YouTubeSearchEngine(gemini_api_key=args.api_key)
    
    # Create index if requested
    if args.create_index:
        if not os.path.exists(args.csv):
            print(f"❌ CSV file not found: {args.csv}")
            sys.exit(1)
        
        success = search_engine.load_or_create_index(args.csv, force_create=True)
        if not success:
            print("❌ Failed to create index")
            sys.exit(1)
    
    # Interactive mode
    if args.interactive:
        search_engine.interactive_search()
        return
    
    # Single search mode
    if args.query:
        # Load or create index if needed
        if not search_engine.vector_store:
            csv_path = args.csv if os.path.exists(args.csv) else '../master_dataset_embedded.csv'
            search_engine.load_or_create_index(csv_path)
        
        # Perform search
        results = search_engine.search(
            query=args.query,
            top_k=args.top_k,
            include_summary=not args.no_summary
        )
        
        # Output results
        search_engine.print_results(results, args.output)
    
    else:
        print("\nUsage examples:")
        print("  python youtube_search.py --query \"machine learning tutorial\"")
        print("  python youtube_search.py --create-index --csv \"path/to/dataset.csv\"")
        print("  python youtube_search.py --interactive")
        print("\nFor more options: python youtube_search.py --help")


if __name__ == "__main__":
    # Check requirements
    try:
        import langchain_community
        import pandas
    except ImportError:
        print("❌ Required packages not installed.")
        print("Install with: pip install langchain-community sentence-transformers faiss-cpu pandas google-generativeai python-dotenv")
        sys.exit(1)
    
    # Run main function
    main()