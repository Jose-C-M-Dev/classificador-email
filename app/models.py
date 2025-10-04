from pydantic import BaseModel, conint
from typing import List

class Classificacao(BaseModel):
    categoria: str
    confianca: conint(ge=0, le=100)
    razao: str

class Resultado(BaseModel):
    arquivo: str
    classificacao: Classificacao
    resposta: str

class ProcessResponse(BaseModel):
    resultados: List[Resultado]
