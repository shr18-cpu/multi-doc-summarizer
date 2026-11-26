from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from document_loader import extract_text
from chunker import split_into_chunks
from embeddings import create_embeddings
from vectorstore import VectorStore
from retriever import retrieve
from summarizer import summarize_document, combine_summaries
from rag import answer_question
import json
from fastapi.responses import StreamingResponse
from llm import generate_response_stream


# =========================================
# FASTAPI APP
# =========================================


app = FastAPI(
    title="Multi-Document Summarizer API",
    description="RAG-based Multi-Document Summarizer using Ollama Qwen3, MiniLM and FAISS",
    version="1.0"
)


# =========================================
# CORS
# =========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# =========================================
# GLOBAL STORAGE
# =========================================

vector_store = VectorStore()
documents = []


# =========================================
# HOME / API STATUS
# =========================================

@app.get("/")
def home():
    return {
        "message": "Multi-Document Summarizer API",
        "status": "running"
    }


# =========================================
# PROCESS DOCUMENTS
# =========================================

@app.post("/process")
async def process_documents(
    files: list[UploadFile] = File(...)
):

    global vector_store
    global documents

    all_chunks = []
    all_metadata = []
    documents = []

    # Process every uploaded document
    for file in files:

        file_bytes = await file.read()

        # -------------------------------------
        # EXTRACT TEXT
        # -------------------------------------

        try:
            text = extract_text(
                file.filename,
                file_bytes
            )

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Error reading {file.filename}: {str(e)}"
            )

        # Ignore empty documents
        if not text.strip():
            continue

        # -------------------------------------
        # CHUNKING
        # 150 words, 30 word overlap
        # -------------------------------------

        chunks = split_into_chunks(
            text,
            chunk_size=150,
            overlap=30
        )

        # -------------------------------------
        # SAVE DOCUMENT
        # -------------------------------------

        documents.append({
            "name": file.filename,
            "text": text,
            "chunks": chunks
        })

        # -------------------------------------
        # SAVE CHUNKS + METADATA
        # -------------------------------------

        for chunk in chunks:

            all_chunks.append(chunk)

            all_metadata.append({
                "source": file.filename
            })

    # -------------------------------------
    # CHECK IF DOCUMENTS EXIST
    # -------------------------------------

    if not all_chunks:
        raise HTTPException(
            status_code=400,
            detail="No usable text found in the uploaded documents."
        )

    # -------------------------------------
    # CREATE MINILM EMBEDDINGS
    # -------------------------------------

    try:

        embeddings = create_embeddings(
            all_chunks
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Embedding generation failed: {str(e)}"
        )

    # -------------------------------------
    # BUILD FAISS VECTOR STORE
    # -------------------------------------

    try:

        vector_store = VectorStore()

        vector_store.build(
            all_chunks,
            all_metadata,
            embeddings
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"FAISS vector store creation failed: {str(e)}"
        )

    # -------------------------------------
    # RESPONSE
    # -------------------------------------

    return {
        "message": "Documents processed successfully",
        "documents": len(documents),
        "chunks": len(all_chunks)
    }


# =========================================
# GET DOCUMENT INFORMATION
# =========================================

@app.get("/documents")
def get_documents():

    if not documents:

        return {
            "documents": []
        }

    document_info = []

    for document in documents:

        document_info.append({
            "name": document["name"],
            "words": len(
                document["text"].split()
            ),
            "chunks": len(
                document["chunks"]
            )
        })

    return {
        "documents": document_info
    }



# =========================================
# GENERATE MULTI-DOCUMENT SUMMARY - STREAMING
# =========================================


@app.post("/summarize")
def summarize():
    if not documents:
        raise HTTPException(
            status_code=400,
            detail="Please process documents first."
        )

    def generate_events():
        try:
            all_summaries = []

            # Tell the frontend generation has started.
            yield json.dumps({
                "type": "status",
                "message": "Starting summary generation..."
            }) + "\n"

            # Begin Overall Summary immediately.
            yield json.dumps({
                "type": "section_start",
                "id": "overall",
                "title": "Overall Summary",
                "message": "Generating Overall Summary..."
            }) + "\n"

            # Stream the summary chunk by chunk.
            for document in documents:
                for chunk in document["chunks"]:
                    prompt = f"""
Summarize this text in 2-4 sentences.
Use only the provided information.

TEXT:
{chunk}
"""
                    chunk_summary = []

                    for token in generate_response_stream(
                        prompt,
                        temperature=0.2,
                        max_tokens=100
                    ):
                        chunk_summary.append(token)

                        yield json.dumps({
                            "type": "token",
                            "id": "overall",
                            "text": token
                        }) + "\n"

                    all_summaries.append(
                        f"Document: {document['name']}\n"
                        + "".join(chunk_summary)
                    )

                    yield json.dumps({
                        "type": "status",
                        "message": (
                            f"Processed a chunk from "
                            f"{document['name']}"
                        )
                    }) + "\n"

            yield json.dumps({
                "type": "section_complete",
                "id": "overall",
                "title": "Overall Summary"
            }) + "\n"

            combined_text = "\n\n".join(all_summaries)

            sections = [
                ("topics", "Main Topics"),
                ("important", "Important Points"),
                ("common", "Common Information"),
                ("differences", "Differences Between Documents"),
                ("conclusion", "Final Conclusion")
            ]

            # Generate the remaining five sections.
            for section_id, title in sections:
                yield json.dumps({
                    "type": "section_start",
                    "id": section_id,
                    "title": title,
                    "message": f"Generating {title}..."
                }) + "\n"

                prompt = f"""
Using only these document summaries, write the
{title} section.

Be clear and concise. Do not invent facts.

DOCUMENT SUMMARIES:
{combined_text}
"""

                for token in generate_response_stream(
                    prompt,
                    temperature=0.2,
                    max_tokens=300
                ):
                    yield json.dumps({
                        "type": "token",
                        "id": section_id,
                        "text": token
                    }) + "\n"

                yield json.dumps({
                    "type": "section_complete",
                    "id": section_id,
                    "title": title
                }) + "\n"

            yield json.dumps({
                "type": "complete",
                "message": "Summary generation complete."
            }) + "\n"

        except Exception as e:
            yield json.dumps({
                "type": "error",
                "message": str(e)
            }) + "\n"

    return StreamingResponse(
        generate_events(),
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )



# =========================================
# QUESTION REQUEST MODEL
# =========================================

class QuestionRequest(BaseModel):

    question: str


# =========================================
# RAG QUESTION ANSWERING
# =========================================


@app.post("/ask")
def ask(request: QuestionRequest):

    # Check if documents have been processed
    if vector_store.index is None:
        raise HTTPException(
            status_code=400,
            detail="Please process documents first."
        )

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Please enter a question."
        )

    # Retrieve relevant document chunks using RAG
    try:
        results = retrieve(
            vector_store,
            question,
            top_k=3
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Document retrieval failed: {str(e)}"
        )

    # Build a prompt using the retrieved document content
    context = json.dumps(results, ensure_ascii=False, default=str)

    prompt = f"""
You are a document question-answering assistant.

Answer the question using only the retrieved document information.
Do not invent facts.
If the answer is not supported by the documents, respond:
"Not found in the documents."

Retrieved document information:
{context}

Question:
{question}

Answer clearly and directly.
"""

    # Stream the answer progressively
    def generate_events():
        try:
            for token in generate_response_stream(
                prompt,
                temperature=0.2,
                max_tokens=250
            ):
                yield json.dumps({
                    "type": "token",
                    "text": token
                }) + "\n"

            yield json.dumps({
                "type": "complete"
            }) + "\n"

        except Exception as e:
            yield json.dumps({
                "type": "error",
                "message": str(e)
            }) + "\n"

    return StreamingResponse(
        generate_events(),
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )
