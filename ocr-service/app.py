"""Microservice FastAPI d'extraction et structuration de CV."""

import os
import sys
import shutil
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from paddle_extraction import extract_text
from gemini_paddleocr import structure_cv, structure_cv_from_text_only
from gemini_direct import extract_direct_gemini
from deepseek_paddleocr import structure_cv_deepseek
from groq_paddleocr import structure_cv_groq

app = FastAPI(title="OCR Service - CV Extractor", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}


@app.post("/extract")
async def extract_cv(file: UploadFile = File(...), provider: str = Query("gemini_direct")):
    ext = os.path.splitext(file.filename.lower())[1]

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Format non supporté : {ext} (attendu : {ALLOWED_EXTENSIONS})")

    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, file.filename)

    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        texte_ocr = ""

        if provider in ["gemini_direct", "gemini"]:
            try:
                structured = extract_direct_gemini(temp_path)
            except Exception as error:
                raise HTTPException(500, f"Erreur Gemini Direct : {error}")

        elif provider == "paddle_gemini":
            try:
                texte_ocr = extract_text(temp_path)
                structured = structure_cv_from_text_only(texte_ocr)
            except Exception as error:
                raise HTTPException(500, f"Erreur PaddleOCR + Gemini Texte-Seul : {error}")

        elif provider in ["paddle_groq", "groq_paddleocr", "groq"] or "groq" in provider:
            try:
                texte_ocr = extract_text(temp_path)
            except Exception as error:
                raise HTTPException(500, f"Erreur PaddleOCR : {error}")

            if not texte_ocr.strip():
                raise HTTPException(422, "Aucun texte détecté par l'OCR, et Groq nécessite le texte OCR.")

            try:
                structured = structure_cv_groq(texte_ocr)
            except Exception as error:
                raise HTTPException(500, f"Erreur Groq : {error}")

        elif provider in ["paddle_deepseek", "deepseek_paddleocr", "deepseek"] or "deepseek" in provider:
            try:
                texte_ocr = extract_text(temp_path)
            except Exception as error:
                raise HTTPException(500, f"Erreur PaddleOCR : {error}")

            if not texte_ocr.strip():
                raise HTTPException(422, "Aucun texte détecté par l'OCR, et DeepSeek nécessite le texte OCR.")

            try:
                structured = structure_cv_deepseek(texte_ocr)
            except RuntimeError as error:
                err_msg = str(error)
                if "402" in err_msg or "Solde" in err_msg:
                    raise HTTPException(402, err_msg)
                raise HTTPException(500, f"Erreur DeepSeek : {err_msg}")
            except Exception as error:
                raise HTTPException(500, f"Erreur DeepSeek : {error}")

        else:
            try:
                texte_ocr = extract_text(temp_path)
            except Exception as error:
                texte_ocr = ""

            try:
                structured = structure_cv(texte_ocr, temp_path)
            except Exception as error:
                raise HTTPException(500, f"Erreur structuration ({provider}) : {error}")

        structured["_meta"] = {
            "provider": provider,
            "filename": file.filename,
            "ocr_text_length": len(texte_ocr),
        }

        return structured

    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(500, str(error))
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


@app.get("/health")
def health():
    return {"status": "ok", "service": "ocr-service", "pipeline": ["paddleocr", "gemini|groq|deepseek"]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)