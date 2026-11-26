from summarizer import ask_llm


def answer_question(
    question,
    retrieved_chunks
):

    if not retrieved_chunks:

        return (
            "Not found in the documents."
        )


    context_parts = []


    for i, result in enumerate(
        retrieved_chunks
    ):

        source = result[
            "metadata"
        ].get(
            "source",
            "Unknown document"
        )


        context_parts.append(
            f"""
SOURCE {i + 1}: {source}

DOCUMENT TEXT:
{result["chunk"]}
"""
        )


    context = "\n\n".join(
        context_parts
    )


    prompt = f"""
You are a document question-answering assistant.

Answer the user's question using ONLY
the provided document context.

Rules:

1. Do not use outside knowledge.

2. Do not invent information.

3. If the answer cannot be found in
   the provided context, respond exactly:

Not found in the documents.

4. Give a concise and clear answer.

5. At the end, mention the source
   document(s) used.

DOCUMENT CONTEXT:

{context}

USER QUESTION:

{question}

ANSWER:
"""


    return ask_llm(
    prompt,
    temperature=0.1
)