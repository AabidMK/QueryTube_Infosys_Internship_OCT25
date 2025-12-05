from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

# ------------------ Qdrant Connection ------------------ #
qdrant_client = QdrantClient(
    url="https://63f7ff1e-6ee2-4835-947c-10c1a734cb1e.eu-central-1-0.aws.cloud.qdrant.io",
    api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.-jeQEhiuo5KV5Q3Ha-YfUatW13_iR3olPapJNQqIgwk"
)

# ------------------ Embedding Model ------------------ #
model = SentenceTransformer("intfloat/e5-large-v2")

# ------------------ Search Function ------------------ #
def search_youtube_videos(user_query: str, top_k: int = 5):

    query_vector = model.encode(user_query)

    # IMPORTANT — collection name must match the new 622-video collection
    collection_name = "youtube_videos_full_payload"

    results = qdrant_client.query_points(
        collection_name=collection_name,
        query=query_vector.tolist(),
        with_payload=True,
        limit=top_k
    )

    print(f"\n🔍 User Query: {user_query}")
    print(f"🎯 Top {top_k} Most Relevant Videos:")
    print("-" * 60)

    for i, res in enumerate(results.points, start=1):
        payload = res.payload

        print(f"#{i}")

        print(f"🎬 Title: {payload.get('title', 'N/A')}")
        print(f"📺 Channel: {payload.get('channel_title', 'N/A')}")

        # FIX — your dataset uses `id` as video ID
        print(f"🆔 Video ID: {payload.get('id', 'N/A')}")

        print(f"👁 Views: {payload.get('viewCount', 'N/A')}")
        print(f"⏱ Duration (seconds): {payload.get('duration_seconds', 'N/A')}")
        print(f"🧠 Similarity Score: {round(res.score, 4)}")
        print("-" * 60)


# ------------------ User Input ------------------ #
user_query = input("💭 Enter your search query: ")
search_youtube_videos(user_query)
