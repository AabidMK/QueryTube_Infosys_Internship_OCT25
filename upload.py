# upload.py - Run this on YOUR local machine
import requests
import os

def upload_file_to_render(file_path, render_shell_url):
    """Upload file to Render via curl command"""
    filename = os.path.basename(file_path)
    
    # This generates a curl command you can run in Render Shell
    print(f"To upload {filename}, run this in Render Shell:")
    print(f"cd /opt/render/vectors/faiss_videos_db")
    print(f"echo 'Downloading {filename}...'")
    
    # If you can host files somewhere temporarily
    print(f"# Upload {filename} to any cloud storage and then:")
    print(f"# wget YOUR_DOWNLOAD_LINK -O {filename}")
    
# Run on your local machine
if __name__ == "__main__":
    faiss_path = r"D:\Folders\INFOSYS\vectors\faiss_videos_db\faiss.index"
    metadata_path = r"D:\Folders\INFOSYS\vectors\faiss_videos_db\metadata.pkl"
    
    upload_file_to_render(faiss_path, "")
    print("\n" + "="*50)
    upload_file_to_render(metadata_path, "")