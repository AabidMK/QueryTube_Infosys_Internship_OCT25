# Save as detailed_debug.py
import chromadb
import os
import traceback

def detailed_debug():
    print("🔍 Detailed ChromaDB Debug...")
    
    db_path = "./chroma_videos_db"
    
    try:
        # Create client
        client = chromadb.PersistentClient(path=db_path)
        print("✅ Client created")
        
        # List collections
        collections = client.list_collections()
        print(f"✅ Found {len(collections)} collections")
        
        for i, collection_obj in enumerate(collections):
            print(f"\n🎯 Collection {i+1}: '{collection_obj.name}'")
            print(f"   Type: {type(collection_obj)}")
            print(f"   Methods: {[method for method in dir(collection_obj) if not method.startswith('_')]}")
            
            # Try different ways to access the collection
            print(f"\n   🔧 Testing collection access methods...")
            
            # Method 1: Using the collection object directly
            try:
                print("   Method 1: Direct collection object...")
                count = collection_obj.count()
                print(f"      ✅ Count: {count}")
                
                # Try to get data
                sample = collection_obj.get(limit=1, include=["metadatas", "documents"])
                print(f"      ✅ Data access successful")
                if sample['ids']:
                    print(f"      📝 First item: {sample['ids'][0]}")
                    if sample['metadatas']:
                        print(f"      📊 Metadata: {sample['metadatas'][0]}")
            except Exception as e:
                print(f"      ❌ Method 1 failed: {e}")
            
            # Method 2: Using client.get_collection()
            try:
                print("   Method 2: client.get_collection()...")
                collection = client.get_collection(name=collection_obj.name)
                count = collection.count()
                print(f"      ✅ Count: {count}")
                
                sample = collection.get(limit=1, include=["metadatas", "documents"])
                print(f"      ✅ Data access successful")
                if sample['ids']:
                    print(f"      📝 First item: {sample['ids'][0]}")
            except Exception as e:
                print(f"      ❌ Method 2 failed: {e}")
                print(f"      💡 Full error:")
                traceback.print_exc()
                
    except Exception as e:
        print(f"❌ Overall error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    detailed_debug()