"""
Standalone LangChain Semantic Search Demo

To install:
pip install langchain chromadb sentence-transformers
"""

# 1) Import modules (official docs style)
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document


# -------------------------------
# 2) Load embeddings
# -------------------------------
# This mirrors LangChain docs exactly
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

print("Embeddings model loaded successfully.")

# -------------------------------
# 3) Create sample documents
# -------------------------------
documents = [
    Document(page_content="Deep learning is used for image classification."),
    Document(page_content="Reinforcement learning trains agents using rewards."),
    Document(page_content="Support Vector Machines classify data using hyperplanes."),
    Document(page_content="Neural networks learn patterns from data."),
]

print("Sample documents created.")

# -------------------------------
# 4) Create the vectorstore (Chroma)
# -------------------------------
vectorstore = Chroma.from_documents(
    documents=documents,
    embedding=embeddings,
    collection_name="langchain-demo-store"
)

print("Vector store created.")

# -------------------------------
# 5) Semantic search function
# -------------------------------
def run_semantic_search(query, k=2):
    print(f"\n🔍 Query: {query}")
    results = vectorstore.similarity_search_with_score(query, k=k)

    for doc, score in results:
        print("\nMatched Document →", doc.page_content)
        print("Similarity Score →", score)
        print("-" * 40)


# -------------------------------
# 6) Try some example searches
# -------------------------------
run_semantic_search("How do machines classify images?")
run_semantic_search("What learns from rewards?")
run_semantic_search("Explain SVM.")


print("\n✨ Semantic search demo completed!")
