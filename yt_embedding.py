import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import ast

# Load the dataset
df = pd.read_csv('master_dataset_updated.csv')

# Initialize the embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')  # Fixed typo: 'all-MiniLM-L6-v2'

def combine_title_transcript(row):
    """Combine title and transcript into a single text string"""
    title = row['title']
    transcript = row['transcript']
    
    # Handle missing values - FIXED THIS PART
    if pd.isna(transcript) or transcript == '':
        return title
    else:
        return f"{title} {transcript}"

# Apply the function to create combined text
df['combined_text'] = df.apply(combine_title_transcript, axis=1)

# Generate embeddings
print("Generating embeddings...")
embeddings = model.encode(df['combined_text'].tolist())

# Add embeddings to dataframe
df['embeddings'] = embeddings.tolist()

# Save the updated dataset
df.to_csv('dataset_with_embeddings.csv', index=False)
print("Embeddings generated and saved successfully!")