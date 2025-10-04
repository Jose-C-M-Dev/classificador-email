import os
import json
import re
import asyncio
import httpx
from dotenv import load_dotenv
from typing import List, Dict, Any
from .prompts import get_classification_prompt, get_response_prompt
from .nlp_processor import preprocess_email, extract_keywords

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.1-8b-instant"

USE_NLP_PREPROCESSING = os.getenv("USE_NLP_PREPROCESSING", "true").lower() == "true"

async def _call_groq(messages: List[Dict[str, str]], temperature=0.2, max_tokens=500) -> Any:
    if not GROQ_API_KEY:
        return None

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(API_URL, headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json()


def _parse_classification(raw_text: str) -> Dict[str, Any]:
    try:
        parsed = json.loads(raw_text)
    except Exception:
        m = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if m:
            try:
                parsed = json.loads(m.group(0))
            except Exception:
                parsed = None
        else:
            parsed = None

    if not parsed or not isinstance(parsed, dict):
        return {
            "categoria": "IMPRODUTIVO",
            "confianca": 0,
            "razao": f"Resposta do modelo não foi JSON válido. Trecho: {raw_text[:200]}"
        }

    categoria = str(parsed.get("categoria", "IMPRODUTIVO")).upper()
    try:
        confianca = int(parsed.get("confianca", 0))
    except Exception:
        try:
            confianca = int(float(parsed.get("confianca", 0) or 0))
        except Exception:
            confianca = 0
    razao = str(parsed.get("razao", parsed.get("reason", ""))) or ""
    return {"categoria": categoria, "confianca": max(0, min(confianca, 100)), "razao": razao}


async def classify_one(texto: str) -> Dict[str, Any]:
    nlp_data = None
    texto_para_ai = texto

    if USE_NLP_PREPROCESSING and texto.strip():
        nlp_data = preprocess_email(texto, apply_stem=True)
        keywords = extract_keywords(texto, top_n=5)
        texto_para_ai = f"{texto}\n\n[Palavras-chave identificadas: {', '.join(keywords)}]"

    prompt = get_classification_prompt(texto_para_ai)

    if not GROQ_API_KEY:
        return {
            "categoria": "IMPRODUTIVO",
            "confianca": 0,
            "razao": "GROQ_API_KEY ausente (fallback)",
            "nlp_stats": nlp_data['stats'] if nlp_data else None
        }

    try:
        j = await _call_groq([{"role": "user", "content": prompt}], temperature=0.0, max_tokens=300)
        raw = j["choices"][0]["message"]["content"].strip()
        result = _parse_classification(raw)

        if nlp_data:
            result["nlp_stats"] = nlp_data['stats']
            result["keywords"] = extract_keywords(texto, top_n=5)

        return result
    except httpx.HTTPStatusError as e:
        return {
            "categoria": "IMPRODUTIVO",
            "confianca": 0,
            "razao": f"Erro LLM: {e.response.status_code}",
            "nlp_stats": nlp_data['stats'] if nlp_data else None
        }
    except Exception as e:
        return {
            "categoria": "IMPRODUTIVO",
            "confianca": 0,
            "razao": f"Erro LLM: {str(e)}",
            "nlp_stats": nlp_data['stats'] if nlp_data else None
        }


async def generate_one(texto: str, categoria: str) -> str:
    temperature = 0.5 if categoria == "PRODUTIVO" else 0.3
    max_tokens = 450 if categoria == "PRODUTIVO" else 350

    prompt = get_response_prompt(texto, categoria)

    if not GROQ_API_KEY:
        return ""

    try:
        j = await _call_groq(
            [{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return j["choices"][0]["message"]["content"].strip()
    except Exception:
        return ""


async def process_texts(items: List[Dict[str, str]]) -> List[Dict]:
    classify_tasks = [classify_one(it["texto"]) for it in items]
    classes = await asyncio.gather(*classify_tasks, return_exceptions=True)

    gen_tasks = []
    for it, cls in zip(items, classes):
        if isinstance(cls, Exception):
            categoria = "IMPRODUTIVO"
        else:
            categoria = cls.get("categoria", "IMPRODUTIVO")
        gen_tasks.append(generate_one(it["texto"], categoria))
    responses = await asyncio.gather(*gen_tasks, return_exceptions=True)

    result = []
    for it, cls, resp in zip(items, classes, responses):
        if isinstance(cls, Exception):
            cls = {"categoria": "IMPRODUTIVO", "confianca": 0, "razao": str(cls)}
        if isinstance(resp, Exception):
            resp_text = ""
        else:
            resp_text = str(resp or "")

        nlp_stats = cls.pop("nlp_stats", None) if isinstance(cls, dict) else None
        keywords = cls.pop("keywords", None) if isinstance(cls, dict) else None

        item_result = {
            "arquivo": it.get("arquivo", "texto"),
            "classificacao": {
                "categoria": str(cls.get("categoria", "IMPRODUTIVO")).upper(),
                "confianca": int(cls.get("confianca", 0) or 0),
                "razao": str(cls.get("razao", "") or "")
            },
            "resposta": resp_text
        }

        if nlp_stats:
            item_result["nlp_processing"] = {
                "stats": nlp_stats,
                "keywords": keywords or []
            }

        result.append(item_result)

    return result