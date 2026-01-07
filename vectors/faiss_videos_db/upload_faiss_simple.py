#!/usr/bin/env python3
"""
Upload FAISS index and metadata to Hugging Face Hub (Model Repo)
"""

import os
from huggingface_hub import HfApi, login, create_repo


def main():
    print("=" * 50)
    print("FAISS FILES UPLOAD TO HUGGING FACE")
    print("=" * 50)

    print(f"\nCurrent directory: {os.getcwd()}")

    # Files to upload
    required_files = ["faiss.index", "metadata.pkl"]

    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ ERROR: {file} not found!")
            print("Place this script in the same folder as the files.")
            return
        size_mb = os.path.getsize(file) / 1024 / 1024
        print(f"✅ {file}: {size_mb:.2f} MB")

    # Token login
    print("\nSTEP 1: LOGIN TO HUGGING FACE")
    token = input("Paste your Hugging Face WRITE token: ").strip()
    if not token:
        print("❌ Token is required.")
        return

    try:
        login(token=token)
        print("✅ Login successful!")
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return

    # Repo info
    print("\nSTEP 2: REPOSITORY DETAILS")
    username = input("Your Hugging Face username: ").strip()
    repo_name = input("Repository name (default: faiss-video-db): ").strip()
    if not repo_name:
        repo_name = "faiss-video-db"

    repo_id = f"{username}/{repo_name}"
    print(f"Repository ID: {repo_id}")

    if input("Proceed? (y/n): ").lower() != "y":
        print("❌ Cancelled.")
        return

    # Create repository
    print("\nSTEP 3: CREATING REPOSITORY")
    try:
        create_repo(repo_id=repo_id, repo_type="model", exist_ok=True)
        print("✅ Repository ready.")
    except Exception as e:
        print(f"⚠️ Repo note: {e}")

    api = HfApi()

    # Upload FAISS files
    print("\nSTEP 4: UPLOADING FILES")
    for file in required_files:
        try:
            api.upload_file(
                path_or_fileobj=file,
                path_in_repo=file,
                repo_id=repo_id,
                repo_type="model",
                commit_message=f"Add {file}",
                token=token,
            )
            print(f"✅ Uploaded {file}")
        except Exception as e:
            print(f"❌ Failed to upload {file}: {e}")

    # README content
    print("\nSTEP 5: UPLOADING README")
    try:
        readme = f"""---
license: mit
tags:
- faiss
- vector-search
- embeddings
---

# FAISS Vector Database

This repository contains a FAISS index and metadata for similarity search.

## Files
- `faiss.index` – FAISS vector index
- `metadata.pkl` – Metadata for vectors

## Usage

```python
from huggingface_hub import hf_hub_download
import pickle
import faiss

index_path = hf_hub_download(repo_id="{repo_id}", filename="faiss.index")
metadata_path = hf_hub_download(repo_id="{repo_id}", filename="metadata.pkl")

index = faiss.read_index(index_path)
with open(metadata_path, "rb") as f:
    metadata = pickle.load(f)
```
"""
        api.upload_file(
            path_or_fileobj=readme,
            path_in_repo="README.md",
            repo_id=repo_id,
            repo_type="model",
            commit_message="Add README",
            token=token,
        )
        print("✅ Uploaded README")
    except Exception as e:
        print(f"❌ Failed to upload README: {e}")
    print("\nAll done!")
if __name__ == "__main__":
    main()
   