import sqlite3
import pandas as pd
import json
import ast
import numpy as np
from typing import List, Dict, Any
import os

class SQLiteVideoVectorDB:
    def __init__(self, db_path: str = "video_vectors.db"):
        self.db_path = db_path
        self.conn = None
        self.setup_database()
    
    def setup_database(self):
        """Initialize the database with required tables"""
        self.conn = sqlite3.connect(self.db_path)
        
        # Create main videos table
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS videos (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                transcript TEXT,
                channel_title TEXT,
                view_count REAL,
                duration TEXT,
                published_at TEXT,
                tags TEXT,
                category_id REAL,
                like_count REAL,
                comment_count REAL,
                embeddings_json TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create index for faster searches
        self.conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_view_count 
            ON videos(view_count)
        ''')
        
        self.conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_channel 
            ON videos(channel_title)
        ''')
        
        self.conn.commit()
        print("Database initialized successfully!")
    
    def parse_embeddings(self, embedding_str: str) -> List[float]:
        """Parse embedding string to list of floats"""
        try:
            if isinstance(embedding_str, str):
                # Handle the string representation of list
                return ast.literal_eval(embedding_str)
            elif isinstance(embedding_str, list):
                return embedding_str
            else:
                return []
        except (ValueError, SyntaxError) as e:
            print(f"Error parsing embeddings: {e}")
            return []
    
    def calculate_similarity(self, emb1: List[float], emb2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        if not emb1 or not emb2 or len(emb1) != len(emb2):
            return 0.0
        
        # Convert to numpy arrays for calculation
        a = np.array(emb1)
        b = np.array(emb2)
        
        # Cosine similarity
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)
    
    def import_from_csv(self, csv_file_path: str):
        """Import videos from CSV file into database"""
        if not os.path.exists(csv_file_path):
            print(f"CSV file not found: {csv_file_path}")
            return
        
        df = pd.read_csv(csv_file_path)
        inserted_count = 0
        
        for _, row in df.iterrows():
            try:
                # Parse embeddings
                embeddings = self.parse_embeddings(row['embeddings'])
                
                # Insert into database
                self.conn.execute('''
                    INSERT OR REPLACE INTO videos 
                    (id, title, transcript, channel_title, view_count, duration, 
                     published_at, tags, category_id, like_count, comment_count, embeddings_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row['id'],
                    row['title'],
                    row.get('transcript', ''),
                    row['channel_title'],
                    float(row['viewCount']) if pd.notna(row['viewCount']) else 0.0,
                    row['duration'],
                    row['publishedAt'],
                    row.get('tags', ''),
                    float(row['categoryId']) if pd.notna(row['categoryId']) else 0.0,
                    float(row['likeCount']) if pd.notna(row['likeCount']) else 0.0,
                    float(row['commentCount']) if pd.notna(row['commentCount']) else 0.0,
                    json.dumps(embeddings)  # Store embeddings as JSON string
                ))
                
                inserted_count += 1
                
            except Exception as e:
                print(f"Error inserting video {row['id']}: {e}")
                continue
        
        self.conn.commit()
        print(f"Successfully imported {inserted_count} videos from CSV")
    
    def search_similar_videos(self, query_embedding: List[float], limit: int = 5) -> List[Dict]:
        """Search for videos similar to the query embedding"""
        if not query_embedding:
            return []
        
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, title, transcript, embeddings_json FROM videos')
        
        results = []
        for row in cursor.fetchall():
            video_id, title, transcript, emb_json = row
            
            try:
                video_embedding = json.loads(emb_json)
                similarity = self.calculate_similarity(query_embedding, video_embedding)
                
                results.append({
                    'video_id': video_id,
                    'title': title,
                    'similarity': similarity,
                    'transcript_preview': transcript[:100] + '...' if len(transcript) > 100 else transcript
                })
            except Exception as e:
                continue
        
        # Sort by similarity (highest first) and return top results
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:limit]
    
    def get_video_by_id(self, video_id: str) -> Dict[str, Any]:
        """Get video details by ID"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, title, transcript, channel_title, view_count, duration, 
                   published_at, tags, like_count, comment_count, embeddings_json
            FROM videos WHERE id = ?
        ''', (video_id,))
        
        row = cursor.fetchone()
        if not row:
            return {}
        
        return {
            'video_id': row[0],
            'title': row[1],
            'transcript': row[2],
            'channel_title': row[3],
            'view_count': row[4],
            'duration': row[5],
            'published_at': row[6],
            'tags': row[7],
            'like_count': row[8],
            'comment_count': row[9],
            'embeddings': json.loads(row[10]) if row[10] else []
        }
    
    def get_videos_by_channel(self, channel_title: str, limit: int = 10) -> List[Dict]:
        """Get videos by channel name"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, title, view_count, duration, published_at
            FROM videos 
            WHERE channel_title LIKE ? 
            ORDER BY view_count DESC 
            LIMIT ?
        ''', (f'%{channel_title}%', limit))
        
        return [
            {
                'video_id': row[0],
                'title': row[1],
                'view_count': row[2],
                'duration': row[3],
                'published_at': row[4]
            }
            for row in cursor.fetchall()
        ]
    
    def get_most_viewed_videos(self, limit: int = 10) -> List[Dict]:
        """Get most viewed videos"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, title, channel_title, view_count, duration
            FROM videos 
            ORDER BY view_count DESC 
            LIMIT ?
        ''', (limit,))
        
        return [
            {
                'video_id': row[0],
                'title': row[1],
                'channel_title': row[2],
                'view_count': row[3],
                'duration': row[4]
            }
            for row in cursor.fetchall()
        ]
    
    def get_video_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        cursor = self.conn.cursor()
        
        # Total videos
        cursor.execute('SELECT COUNT(*) FROM videos')
        total_videos = cursor.fetchone()[0]
        
        # Total views
        cursor.execute('SELECT SUM(view_count) FROM videos')
        total_views = cursor.fetchone()[0] or 0
        
        # Average views
        cursor.execute('SELECT AVG(view_count) FROM videos')
        avg_views = cursor.fetchone()[0] or 0
        
        # Unique channels
        cursor.execute('SELECT COUNT(DISTINCT channel_title) FROM videos')
        unique_channels = cursor.fetchone()[0]
        
        return {
            'total_videos': total_videos,
            'total_views': total_views,
            'average_views': round(avg_views, 2),
            'unique_channels': unique_channels
        }
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

def interactive_manager():
    """Interactive command-line interface for managing the video database"""
    db = SQLiteVideoVectorDB("youtube_videos.db")
    
    # Make sure data is imported
    if input("Import data from CSV? (y/n): ").lower() == 'y':
        csv_path = input("Enter CSV file path (default: dataset_with_embeddings.csv): ") or "dataset_with_embeddings.csv"
        db.import_from_csv(csv_path)
    
    while True:
        print("\n" + "="*50)
        print("VIDEO VECTOR DATABASE MANAGER")
        print("="*50)
        print("1. View database statistics")
        print("2. Search most viewed videos")
        print("3. Find videos by channel")
        print("4. Search similar videos (by video ID)")
        print("5. Get video details by ID")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == "1":
            stats = db.get_video_statistics()
            print("\n--- Database Statistics ---")
            for key, value in stats.items():
                print(f"{key.replace('_', ' ').title()}: {value}")
                
        elif choice == "2":
            limit = int(input("How many videos to show? (default: 10): ") or "10")
            videos = db.get_most_viewed_videos(limit)
            print(f"\n--- Top {len(videos)} Most Viewed Videos ---")
            for i, video in enumerate(videos, 1):
                print(f"{i}. {video['title']}")
                print(f"   👁️  {video['view_count']} views | ⏱️  {video['duration']} | 📺 {video['channel_title']}")
                
        elif choice == "3":
            channel = input("Enter channel name to search: ").strip()
            if channel:
                videos = db.get_videos_by_channel(channel, 10)
                print(f"\n--- Videos from '{channel}' ---")
                for i, video in enumerate(videos, 1):
                    print(f"{i}. {video['title']}")
                    print(f"   👁️  {video['view_count']} views | 📅 {video['published_at'][:10]}")
            else:
                print("Please enter a channel name")
                
        elif choice == "4":
            video_id = input("Enter video ID to find similar videos: ").strip()
            if video_id:
                video = db.get_video_by_id(video_id)
                if video:
                    similar_videos = db.search_similar_videos(video['embeddings'], 5)
                    print(f"\n--- Videos similar to: {video['title']} ---")
                    for i, similar in enumerate(similar_videos, 1):
                        print(f"{i}. {similar['title']}")
                        print(f"   🔍 Similarity: {similar['similarity']:.3f}")
                        print(f"   📝 {similar['transcript_preview']}")
                else:
                    print("Video not found!")
            else:
                print("Please enter a video ID")
                
        elif choice == "5":
            video_id = input("Enter video ID: ").strip()
            if video_id:
                video = db.get_video_by_id(video_id)
                if video:
                    print(f"\n--- Video Details ---")
                    print(f"Title: {video['title']}")
                    print(f"Channel: {video['channel_title']}")
                    print(f"Views: {video['view_count']}")
                    print(f"Duration: {video['duration']}")
                    print(f"Published: {video['published_at']}")
                    print(f"Likes: {video['like_count']}")
                    print(f"Comments: {video['comment_count']}")
                    print(f"Tags: {video['tags'][:100]}...")
                else:
                    print("Video not found!")
            else:
                print("Please enter a video ID")
                
        elif choice == "6":
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice. Please try again.")
    
    db.close()

# Run the interactive manager
if __name__ == "__main__":
    interactive_manager()