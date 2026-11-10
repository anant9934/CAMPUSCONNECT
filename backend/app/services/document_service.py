import os
import re
import logging
from typing import List, Dict, Any, Optional
from pypdf import PdfReader
import docx

logger = logging.getLogger(__name__)

# Max file size: 10 MB
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


class DocumentProcessingError(Exception):
    pass


def clean_extracted_text(text: str) -> str:
    """Sanitize and normalize extracted text, neutralizing injection attempts."""
    if not text:
        return ""
    # Strip null bytes and non-printable characters
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    # Neutralize prompt injection markers if present in raw document
    text = re.sub(r'(?i)(ignore previous instructions|system instruction|override prompt)', r'[redacted-marker]', text)
    # Normalize multiple newlines and whitespace
    text = re.sub(r'\r\n|\r', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]{2,}', ' ', text)
    return text.strip()


def extract_text_from_pdf(file_path: str) -> List[Dict[str, Any]]:
    """Extract page-indexed text from a PDF file."""
    pages = []
    try:
        reader = PdfReader(file_path)
        for idx, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            clean_text = clean_extracted_text(page_text)
            if clean_text:
                pages.append({"page_number": idx + 1, "text": clean_text})
    except Exception as e:
        logger.error(f"Failed to read PDF {file_path}: {e}")
        raise DocumentProcessingError(f"Could not parse PDF document: {str(e)}")
    return pages


def extract_text_from_docx(file_path: str) -> List[Dict[str, Any]]:
    """Extract text from a DOCX file."""
    try:
        doc = docx.Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            if para.text.strip():
                full_text.append(para.text.strip())
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_text:
                    full_text.append(row_text)
        
        joined = "\n\n".join(full_text)
        cleaned = clean_extracted_text(joined)
        return [{"page_number": 1, "text": cleaned}] if cleaned else []
    except Exception as e:
        logger.error(f"Failed to read DOCX {file_path}: {e}")
        raise DocumentProcessingError(f"Could not parse Word document: {str(e)}")


def extract_text_from_txt(file_path: str) -> List[Dict[str, Any]]:
    """Extract text from a plain TXT file."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        cleaned = clean_extracted_text(content)
        return [{"page_number": 1, "text": cleaned}] if cleaned else []
    except Exception as e:
        logger.error(f"Failed to read TXT {file_path}: {e}")
        raise DocumentProcessingError(f"Could not parse Text document: {str(e)}")


def chunk_text(
    pages: List[Dict[str, Any]],
    chunk_size: int = 500,
    chunk_overlap: int = 100
) -> List[Dict[str, Any]]:
    """Split extracted page text into overlapping semantic chunks with page tracking."""
    chunks = []
    chunk_idx = 0

    for page_item in pages:
        page_num = page_item["page_number"]
        text = page_item["text"]
        
        # Split by paragraphs or sentences
        paragraphs = text.split("\n\n")
        current_chunk = ""
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            if len(current_chunk) + len(para) + 2 <= chunk_size:
                current_chunk = f"{current_chunk}\n\n{para}".strip()
            else:
                if current_chunk:
                    chunks.append({
                        "chunk_index": chunk_idx,
                        "content": current_chunk,
                        "clean_text": current_chunk.lower(),
                        "page_number": page_num,
                        "token_count": len(current_chunk.split()),
                    })
                    chunk_idx += 1
                
                # If paragraph itself is larger than chunk_size, split by characters/words
                if len(para) > chunk_size:
                    words = para.split()
                    sub_chunk = ""
                    for w in words:
                        if len(sub_chunk) + len(w) + 1 <= chunk_size:
                            sub_chunk = f"{sub_chunk} {w}".strip()
                        else:
                            if sub_chunk:
                                chunks.append({
                                    "chunk_index": chunk_idx,
                                    "content": sub_chunk,
                                    "clean_text": sub_chunk.lower(),
                                    "page_number": page_num,
                                    "token_count": len(sub_chunk.split()),
                                })
                                chunk_idx += 1
                            sub_chunk = w
                    current_chunk = sub_chunk
                else:
                    current_chunk = para
        
        if current_chunk:
            chunks.append({
                "chunk_index": chunk_idx,
                "content": current_chunk,
                "clean_text": current_chunk.lower(),
                "page_number": page_num,
                "token_count": len(current_chunk.split()),
            })
            chunk_idx += 1

    return chunks


def process_document_file(file_path: str, mime_type: str) -> List[Dict[str, Any]]:
    """Validates file, extracts text, cleans, and creates chunks."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise DocumentProcessingError(f"Unsupported file format '{ext}'. Allowed: .pdf, .docx, .txt")

    if not os.path.exists(file_path):
        raise DocumentProcessingError("File not found on server.")

    size = os.path.getsize(file_path)
    if size > MAX_FILE_SIZE_BYTES:
        raise DocumentProcessingError(f"File size ({size} bytes) exceeds limit of 10MB.")

    if ext == ".pdf":
        pages = extract_text_from_pdf(file_path)
    elif ext == ".docx":
        pages = extract_text_from_docx(file_path)
    elif ext == ".txt":
        pages = extract_text_from_txt(file_path)
    else:
        raise DocumentProcessingError("Unsupported document format.")

    if not pages:
        raise DocumentProcessingError("No readable text found in document.")

    return chunk_text(pages)

