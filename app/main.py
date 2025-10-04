from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from .models import ProcessResponse
from .file_processor import process_files
from .ai_service import process_texts
import os

app = FastAPI(title="AutoEmail - Classificador")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    path = os.path.join("static", "index.html")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


@app.post("/process", response_model=ProcessResponse)
async def process_email(
    texto: Optional[str] = Form(None),
    arquivo: Optional[List[UploadFile]] = File(None)
):
    resultados = []

    if arquivo:
        resultados.extend(await process_files(arquivo))

    if texto and texto.strip():
        resultados.extend(await process_texts([{"arquivo": "texto", "texto": texto.strip()}]))

    if not resultados:
        raise HTTPException(status_code=400, detail="Nenhum arquivo ou texto enviado.")

    return ProcessResponse(resultados=resultados)
