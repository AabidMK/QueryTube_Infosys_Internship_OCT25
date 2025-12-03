import pandas as pd
import ast
import chromadb
from tqdm import tqdm 

# --- Configuration ---
# NOTE: Update FILE_NAME to the absolute path shown in your error message
FILE_NAME ="INPUT_FILE_PATH"
VECTOR_DB_PATH = "DATABASE_PATH"
COLLECTION_NAME = 'COLLECTION_NAME'

# Columns to be used. Note: ALL names will be converted to lowercase by the script.
REQUIRED_COLUMNS = [
    'id', 
    'transcript', 
    'embedding', 
    'title', 
    'channel_title', 
    'viewcount',    # Matches your full list
    'duration'      # Matches your full list
]
ID_COL = 'id'

# --- 1. Load and Process Data ---
try:
    # Use low_memory=False to potentially handle the mixed types warning better
    df = pd.read_csv(FILE_NAME, low_memory=False)
    print(f"File '{FILE_NAME}' loaded successfully.")
    
    # CRITICAL: Normalize ALL column names to lowercase and strip whitespace
    df.columns = df.columns.str.strip().str.lower()
    print("DataFrame column names normalized.")

    # Select only the required columns and make a copy
    # We ensure we select the lowercase version of the column names
    df_data = df[[col.lower() for col in REQUIRED_COLUMNS]].copy()

    # --- CRITICAL FIX: Ensure Unique IDs and Convert Embedding Type ---
    
    # 1. Remove rows with duplicate IDs
    initial_count = len(df_data)
    df_data.drop_duplicates(subset=[ID_COL], keep='first', inplace=True)
    duplicates_removed = initial_count - len(df_data)
    if duplicates_removed > 0:
        print(f"Removed {duplicates_removed} rows due to duplicate IDs.")

    # 2. Convert the string representation of the embedding list back into a list of floats
    df_data['embedding'] = df_data['embedding'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    
    print("Data processed and embeddings converted to list format.")

except Exception as e:
    # Print the full list of columns found in the DataFrame to aid debugging
    if 'df' in locals():
        print(f"\nDebug Info: Columns found in DataFrame: {df.columns.tolist()}")
    print(f"\nAn error occurred during data loading/processing: {e}")
    raise SystemExit(1)


# --- 2. Prepare Data for ChromaDB ---
embeddings_list = df_data['embedding'].tolist()
documents_list = df_data['transcript'].tolist()

# Create a list of metadata dictionaries
metadatas_list = []
for index, row in df_data.iterrows():
    metadata = {
        'title': row['title'],
        'channel_title': row['channel_title'],
        # Ensure all columns exist and handle potential NaN/missing values
        'view_count': int(row['viewcount']) if pd.notna(row['viewcount']) else 0, 
        'duration': row['duration']
    }
    metadatas_list.append(metadata)

# Create unique IDs
ids_list = df_data[ID_COL].astype(str).tolist()

print(f"Data prepared: {len(ids_list)} unique records ready for insertion.")


# --- 3. Initialize ChromaDB Client and Collection ---
client = chromadb.PersistentClient(path=VECTOR_DB_PATH)

try:
    client.delete_collection(name=COLLECTION_NAME)
    print(f"Existing collection '{COLLECTION_NAME}' deleted for clean upload.")
except:
    pass 

collection = client.get_or_create_collection(
    name=COLLECTION_NAME
)
print(f"ChromaDB collection '{COLLECTION_NAME}' initialized.")


# --- 4. Add Data to ChromaDB (Batch Upload) ---
BATCH_SIZE = 500
total_records = len(ids_list)

print(f"Starting batch upload (Total records: {total_records}, Batch size: {BATCH_SIZE})...")

for i in tqdm(range(0, total_records, BATCH_SIZE), desc="Uploading Batches"):
    start = i
    end = min(i + BATCH_SIZE, total_records)
    
    try:
        collection.add(
            embeddings=embeddings_list[start:end],
            documents=documents_list[start:end],
            metadatas=metadatas_list[start:end],
            ids=ids_list[start:end]
        )
    except Exception as e:
        print(f"\n❌ Error during batch upload for index {start} to {end}: {e}")
        
print(f"\n✅ Successfully saved {collection.count()} records to ChromaDB at: {VECTOR_DB_PATH}")