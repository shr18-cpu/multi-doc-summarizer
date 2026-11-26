import faiss
import numpy as np


class VectorStore:

    def __init__(self):
        self.index = None
        self.chunks = []
        self.metadata = []

    def build(self, chunks, metadata, embeddings):

        embeddings = np.asarray(
            embeddings,
            dtype="float32"
        )

        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatIP(dimension)

        self.index.add(embeddings)

        self.chunks = chunks
        self.metadata = metadata

    def search(self, query_embedding, top_k=5):

        query_embedding = np.asarray(
            query_embedding,
            dtype="float32"
        )

        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)

        scores, indices = self.index.search(
            query_embedding,
            top_k
        )

        results = []

        for score, index in zip(
            scores[0],
            indices[0]
        ):

            if index == -1:
                continue

            results.append({
                "chunk": self.chunks[index],
                "metadata": self.metadata[index],
                "score": float(score)
            })

        return results