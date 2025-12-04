# AI-QueryTube 

**AI-QueryTube** is an AI-powered semantic search and summarization tool designed for video content. It allows users to search through video transcripts using natural language queries and retrieve relevant video segments along with concise summaries.

This project utilizes vector embeddings and similarity search to find specific moments in videos, making it easier to navigate large educational or informational video datasets.

## Features

* **Semantic Search:** Uses vector embeddings to understand the *meaning* of a query, not just keyword matching.
* **Vector Database Integration:** Implements FAISS (Facebook AI Similarity Search) for high-speed retrieval of relevant transcripts.
* **Video Summarization:** Generates summaries of the retrieved content (via `summary.py`).
* **Web Interface:** A user-friendly Flask web application for entering queries and viewing results.
* **Data Processing Pipeline:** Includes Jupyter notebooks and scripts for cleaning datasets and generating embeddings.

## Tech Stack

* **Language:** Python 3.x
* **Web Framework:** Flask
* **Machine Learning:** FAISS (Vector DB), Embeddings (Transformers)
* **Data Handling:** Pandas, NumPy, Pickle
* **Frontend:** HTML, CSS, JavaScript

## Project Structure

Here is an overview of the key files in the repository:

| File/Folder | Description |
| :--- | :--- |
| `app.py` | The main entry point for the Flask web application. |
| `search.py` | Contains logic to query the vector database and return relevant results. |
| `summary.py` | Script responsible for generating summaries of the found content. |
| `Vector_db_Faiss.ipynb`| Jupyter Notebook used to generate embeddings and build the FAISS index. |
| `final_embeddings.index`| The generated FAISS index file containing vector embeddings. |
| `final_metadata.pkl` | Pickled metadata file linking embeddings to video details (titles, URLs). |
| `dataset_with_embeddings.csv` | Intermediate dataset containing transcripts and their vector representations. |
| `Video_transcripts/` | Directory containing raw transcript text files. |
| `templates/` & `static/` | Frontend HTML templates and static assets (CSS/JS). |
| `AI-QueryTube AI.pdf` | Project documentation and report. |

##  Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/Ramya-Kadali/AI-QueryTube.git](https://github.com/Ramya-Kadali/AI-QueryTube.git)
    cd AI-QueryTube
    ```

2.  **Create a Virtual Environment**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies**
    *(Note: Ensure you have `requirements.txt`. If not, install the core libraries manually)*
    ```bash
    pip install flask pandas numpy faiss-cpu sentence-transformers scikit-learn
    ```

4.  **Run the Application**
    ```bash
    python app.py
    ```
    The application will typically run at `http://127.0.0.1:5000/`.

## Usage

1.  Open the web interface in your browser.
2.  Enter a question or topic in the search bar (e.g., *"Python"*).
3.  The system will search the `final_embeddings.index` using the logic in `search.py`.
4.  It will display the most relevant video segments and a generated summary.

