from sentence_transformers import SentenceTransformer

# Load E5 model once at startup
model = SentenceTransformer("intfloat/e5-large-v2")

def embed_text(text: str):
    return model.encode(text, convert_to_numpy=True).tolist()
