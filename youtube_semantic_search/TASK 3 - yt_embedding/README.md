# YouTube Video Embedding Generator (TF-IDF + SVD)

## 📘 Overview
This project generates **numerical embeddings** for YouTube videos based on their **title** and **transcript**.  
The embeddings are created using a combination of **TF-IDF (Term Frequency–Inverse Document Frequency)** and **Truncated SVD (Latent Semantic Analysis)** to reduce dimensionality and capture meaningful semantic relationships between videos.

The output is a CSV file containing original video metadata and a new `text_embedding` column representing each video as a 100-dimensional vector.

---

## ⚙️ Steps Performed

### 1. Load the Dataset
The script loads the CSV file containing YouTube video data:
```python
file_name = "G:\infosys_internship\yt_embedding\cleaned_youtube_details.csv"
df = pd.read_csv(file_name)
```
The file is expected to contain at least the following columns:
- `video_id`
- `title`
- `transcript`

---

### 2. Preprocess and Combine Text
Missing transcript values are filled with empty strings, and both the **title** and **transcript** are combined into a single column:
```python
df['transcript'] = df['transcript'].fillna('')
df['combined_text'] = df['title'].astype(str) + " [SEP] " + df['transcript'].astype(str)
```
This ensures the model has unified text data to learn from both metadata and spoken content.

---

### 3. Generate Text Embeddings

#### a. TF-IDF Vectorization
Transforms the combined text into a sparse matrix of weighted word frequencies:
```python
tfidf_vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
tfidf_matrix = tfidf_vectorizer.fit_transform(df['combined_text'])
```
- `stop_words='english'` removes common English words.  
- `max_features=5000` limits vocabulary size for efficiency.

#### b. Dimensionality Reduction with Truncated SVD
Reduces TF-IDF vectors from thousands of features to **100 meaningful dimensions**:
```python
svd_model = TruncatedSVD(n_components=100, random_state=42)
embedding_matrix = svd_model.fit_transform(tfidf_matrix)
```

---

### 4. Store Embeddings in DataFrame
Each 100-dimensional vector is converted to a Python list and stored as a new column:
```python
df['text_embedding'] = [list(vec) for vec in embedding_matrix]
```

---

### 5. Save Results to CSV
The enriched dataset is saved as:
```python
output_file_name = "G:\infosys_internship\yt_embedding\youtube_details_with_embeddings.csv"
df.to_csv(output_file_name, index=False)
```

The output CSV now includes:
- `video_id`
- `title`
- `transcript`
- `combined_text`
- `text_embedding` (list of 100 float values)

---

## 🧩 Example Output (simplified)

| video_id | title | transcript | text_embedding |
|-----------|--------|-------------|----------------|
| abc123 | How to plant tomatoes | Welcome to my gardening tutorial... | [0.021, 0.114, -0.053, ...] |
| xyz456 | Python Tutorial for Beginners | Today we’ll learn about loops... | [0.009, 0.127, 0.066, ...] |

---

## 🧠 Use Cases
- Semantic video search  
- Clustering similar videos  
- Recommendation systems  
- Topic modeling and categorization  

---

## 🧰 Requirements
Install the required Python libraries:
```bash
pip install pandas scikit-learn
```

---

## 📍 File Paths
Update file paths as per your environment:
- Input file: `cleaned_youtube_details.csv`
- Output file: `youtube_details_with_embeddings.csv`

---

## 👨‍💻 Author
Developed by **M. Shalom Vishal** during the **Infosys Internship** project for YouTube video analysis and embedding generation.
