from qdrant_client import QdrantClient

qdrant = QdrantClient(
    url="https://63f7ff1e-6ee2-4835-947c-10c1a734cb1e.eu-central-1-0.aws.cloud.qdrant.io",
    api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.-jeQEhiuo5KV5Q3Ha-YfUatW13_iR3olPapJNQqIgwk"
)

collection = "youtube_videos"

results = qdrant.scroll(
    collection_name=collection,
    limit=10,
    with_payload=True
)

print("\n📌 First 10 stored video_ids:\n")
for point in results[0]:
    print(point.payload.get("video_id"))
