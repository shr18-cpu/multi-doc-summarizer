from llm import generate_response


# =========================================
# LLM CONNECTION
# =========================================

def ask_llm(prompt, temperature=0.2, max_tokens=500):

    return generate_response(
        prompt,
        temperature=temperature,
        max_tokens=max_tokens
    )


# =========================================
# SUMMARIZE INDIVIDUAL CHUNK
# =========================================

def summarize_chunk(chunk):

    prompt = f"""
Summarize the following document content.

Rules:
- Include only important information.
- Preserve names, facts, dates and numbers.
- Do not add information.
- Use simple and concise language.

CONTENT:
{chunk}

SUMMARY:
"""

    return ask_llm(
        prompt,
        temperature=0.2,
        max_tokens=250
    )


# =========================================
# SUMMARIZE DOCUMENT IN BATCHES
# =========================================

def summarize_document(chunks):

    summaries = []

    batch_size = 5

    total_batches = (
        len(chunks) + batch_size - 1
    ) // batch_size

    for i in range(0, len(chunks), batch_size):

        batch = chunks[i:i + batch_size]

        print(
            f"Processing batch "
            f"{(i // batch_size) + 1}/{total_batches}"
        )

        document_text = "\n\n".join(
            f"CHUNK {j + 1}:\n{chunk}"
            for j, chunk in enumerate(batch)
        )

        prompt = f"""
Create a concise summary of the following document chunks.

Instructions:
- Cover the important information from every chunk.
- Preserve important facts, names, dates and numbers.
- Remove repeated information.
- Do not invent facts.
- Use clear and simple language.
- Do not skip important information.

DOCUMENT:
{document_text}

SUMMARY:
"""

        summary = ask_llm(
            prompt,
            temperature=0.2,
            max_tokens=400
        )

        summaries.append(summary)

    print("All document batches summarized!")

    return "\n\n".join(summaries)


# =========================================
# COMBINE MULTIPLE DOCUMENT SUMMARIES
# =========================================

def combine_summaries(document_summaries):

    if isinstance(document_summaries, list):
        document_summaries = "\n\n".join(
            document_summaries
        )

    prompt = f"""
Create one consolidated summary from the following
document summaries.

Use these six sections:

1. Overall Summary
2. Main Topics
3. Important Points
4. Common Information
5. Differences Between Documents
6. Final Conclusion

Rules:
- Use only the provided information.
- Preserve important facts, numbers and dates.
- Include information from all documents.
- Mention differences only when supported.
- Avoid repetition.
- Use clear and concise language.

DOCUMENT SUMMARIES:
{document_summaries}

FINAL SUMMARY:
"""

    return ask_llm(
        prompt,
        temperature=0.2,
        max_tokens=700
    )