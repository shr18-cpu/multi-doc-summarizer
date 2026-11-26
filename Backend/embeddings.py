from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"


model = SentenceTransformer(
    MODEL_NAME
)


def create_embeddings(texts):

    if not texts:
        return []

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False
    )

    return embeddings