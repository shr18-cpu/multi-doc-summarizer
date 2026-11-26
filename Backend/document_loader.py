import io
import fitz
from docx import Document


def extract_pdf(file_bytes):
    text = ""

    pdf = fitz.open(stream=file_bytes, filetype="pdf")

    for page in pdf:
        page_text = page.get_text()

        if page_text.strip():
            text += page_text + "\n"

    pdf.close()

    return text


def extract_docx(file_bytes):
    document = Document(io.BytesIO(file_bytes))

    text = ""

    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            text += paragraph.text + "\n"

    return text


def extract_txt(file_bytes):
    return file_bytes.decode("utf-8", errors="ignore")


def extract_text(filename, file_bytes):

    filename = filename.lower()

    if filename.endswith(".pdf"):
        return extract_pdf(file_bytes)

    elif filename.endswith(".docx"):
        return extract_docx(file_bytes)

    elif filename.endswith(".txt"):
        return extract_txt(file_bytes)

    else:
        raise ValueError("Unsupported file format")