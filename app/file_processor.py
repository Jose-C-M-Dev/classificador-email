from typing import List, Dict
from fastapi import UploadFile
from io import BytesIO
from PyPDF2 import PdfReader
from .ai_service import process_texts

def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    name = (filename or "").lower()
    if name.endswith(".txt"):
        try:
            return file_bytes.decode("utf-8", errors="ignore")
        except Exception:
            return file_bytes.decode("latin-1", errors="ignore")
    elif name.endswith(".pdf"):
        try:
            pdf_stream = BytesIO(file_bytes)
            pdf = PdfReader(pdf_stream)
            return " ".join(page.extract_text() or "" for page in pdf.pages)
        except Exception:
            return ""
    else:
        return ""


async def process_files(upload_files: List[UploadFile]) -> List[Dict]:
    itens = []
    for f in upload_files:
        raw = await f.read()
        texto = extract_text_from_file(raw, f.filename or "sem_nome")
        itens.append({"arquivo": f.filename or "sem_nome", "texto": texto})
    return await process_texts(itens)
