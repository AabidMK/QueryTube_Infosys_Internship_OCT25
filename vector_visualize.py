import sqlite3
import os

def check_chroma_database():
    print("🔍 DIRECT DATABASE INSPECTION")
    print("=" * 40)
    
    db_path = "./chroma_videos_db/chroma.sqlite3"
    
    if not os.path.exists(db_path):
        print("❌ Database file doesn't exist!")
        return
    
    print(f"📁 Database file: {db_path}")
    print(f"📊 File size: {os.path.getsize(db_path)} bytes")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # List all tables
        print("\n📋 Database tables:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for table in tables:
            print(f"  - {table[0]}")
        
        # Check collections table
        print("\n🔍 Checking collections table:")
        cursor.execute("SELECT COUNT(*) FROM collections;")
        collection_count = cursor.fetchone()[0]
        print(f"  Collections count: {collection_count}")
        
        if collection_count > 0:
            cursor.execute("SELECT name, id FROM collections;")
            collections = cursor.fetchall()
            for name, col_id in collections:
                print(f"  - Collection: '{name}' (ID: {col_id})")
        
        # Check embeddings table (this is where the data is stored)
        print("\n🔍 Checking embeddings table:")
        cursor.execute("SELECT COUNT(*) FROM embeddings;")
        embedding_count = cursor.fetchone()[0]
        print(f"  Total embeddings stored: {embedding_count}")
        
        if embedding_count > 0:
            # Get some sample data
            cursor.execute("SELECT collection_id, id, embedding FROM embeddings LIMIT 3;")
            samples = cursor.fetchall()
            print(f"  Sample embeddings: {len(samples)}")
            for sample in samples:
                print(f"    - Collection ID: {sample[0]}, Item ID: {sample[1]}")
        
        conn.close()
        
        print(f"\n🎯 CONCLUSION:")
        if embedding_count > 0:
            print(f"✅ DATABASE HAS DATA: {embedding_count} embeddings stored")
        else:
            print(f"❌ DATABASE IS EMPTY: No embeddings found")
            
    except Exception as e:
        print(f"❌ Error reading database: {e}")

if __name__ == "__main__":
    check_chroma_database()