
import pandas as pd

# Read the CSV file — use quotes for the filename
df = pd.read_csv("enriched_data_with_chunked_embeddings.csv")

# Print all column names
print(df.columns)

# Show first 20 rows of selected columns — use quotes for column names
print(df[["id", "title", "viewCount"]].head(20))

# Count how many rows have missing (NaN) 'viewCount'
print(df["viewCount"].isna().sum(), "rows have NaN viewCount")

# Show the data type of 'viewCount'
print(df["viewCount"].dtype)
