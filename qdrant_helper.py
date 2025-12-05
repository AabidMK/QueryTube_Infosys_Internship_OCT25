from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, PointStruct
import uuid

collection_name = "youtube_videos_RS"

# Qdrant connection
qdrant = QdrantClient(
    url="https://63f7ff1e-6ee2-4835-947c-10c1a734cb1e.eu-central-1-0.aws.cloud.qdrant.io",
    api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.-jeQEhiuo5KV5Q3Ha-YfUatW13_iR3olPapJNQqIgwk",
)

# Ensure collection exists
def init_collection(dim: int):
    if not qdrant.collection_exists(collection_name):
        qdrant.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=dim, distance="Cosine")
        )
        print("✅ Collection created:", collection_name)
    else:
        print("ℹ️ Collection exists:", collection_name)


def upsert_record(vector, payload: dict):
    point = PointStruct(
        id=str(uuid.uuid4()),
        vector=vector,
        payload=payload
    )

    qdrant.upsert(
        collection_name=collection_name,
        points=[point]
    )

    return True
