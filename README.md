# DocuMind – Multi-Document Summarizer and Question Answering System

## Overview

DocuMind is an AI-powered application that allows users to upload multiple documents, generate consolidated summaries, and ask questions based on their document content.

It uses **Ollama (Qwen3:4B)** for local language model inference and **Retrieval-Augmented Generation (RAG)** to provide context-based answers. The application also supports progressive summary streaming, allowing users to view generated summary text as it arrives.

## Features

- **Multi-Document Upload:** Upload and process multiple documents.
- **AI-Powered Summarization:** Generate consolidated summaries from uploaded documents.
- **Progressive Summary Streaming:** Display summary text progressively using Server-Sent Events (SSE).
- **Six-Section Summary:** Organizes summaries into:
  1. Overall Summary
  2. Main Topics
  3. Important Points
  4. Common Information
  5. Differences Between Documents
  6. Final Conclusion
- **RAG-Based Question Answering:** Ask questions and receive answers based on uploaded documents.
- **Semantic Search:** Retrieve relevant information using document embeddings.
- **FAISS Vector Storage:** Efficiently store and retrieve document embeddings.
- **Local LLM Integration:** Uses Ollama with Qwen3:4B.

## Technologies Used

- Python
- FastAPI
- HTML, CSS, JavaScript
- Ollama – Qwen3:4B
- Retrieval-Augmented Generation (RAG)
- FAISS
- Document Embeddings
- Server-Sent Events (SSE)

## Project Structure

```text
GenAI_Project/
│
├── Backend/
│   ├── app.py
│   ├── document_loader.py
│   ├── chunker.py
│   ├── embeddings.py
│   ├── vectorstore.py
│   ├── retriever.py
│   ├── rag.py
│   ├── summarizer.py
│   ├── llm.py
│   └── requirements.txt
│
├── Frontend/
│   ├── index.html
│   ├── app.js
│   └── style.css
│
└── README.md
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd GenAI_Project
```

### 2. Set Up the Backend

```bash
cd Backend
python -m venv venv
```

Activate the virtual environment:

**Windows:**
```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Set Up Ollama

Install Ollama and download the Qwen3:4B model:

```bash
ollama pull qwen3:4b
```

### 4. Run the Backend

From the Backend directory:

```bash
uvicorn app:app --reload
```

Backend URL: `http://127.0.0.1:8000`

### 5. Run the Frontend

Open another terminal:

```bash
cd Frontend
python -m http.server 5500
```

Open the application in your browser:

`http://localhost:5500`

## How to Use

1. Start Ollama and run the Qwen3:4B model.
2. Start the FastAPI backend and frontend server.
3. Upload multiple documents.
4. Process the uploaded documents.
5. Generate a consolidated summary.
6. View the summary progressively as it is generated.
7. Enter questions to retrieve relevant answers from the uploaded documents.

## Future Improvements

- Support for additional document formats.
- Improved summary customization.
- Enhanced retrieval accuracy.
- Better document comparison and analysis.
- Improved streaming experience during document batch summarization.

## Author

Developed as an AI-based document summarization and question-answering project.
