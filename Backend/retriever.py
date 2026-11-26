from embeddings import create_embeddings


def retrieve(store, question, top_k=5):

    query_embedding = create_embeddings(
        [question]
    )

    results = store.search(
        query_embedding,
        top_k=top_k
    )

    return results