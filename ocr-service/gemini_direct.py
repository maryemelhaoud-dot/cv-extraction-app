"""Extraction directe de CV via Gemini Vision."""

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gemini_paddleocr import RESPONSE_SCHEMA, _guess_mime_type

load_dotenv()

def _get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY manquant dans le fichier .env")
    return genai.Client(api_key=api_key)

PROMPT_DIRECT = """Tu es un expert en extraction et analyse automatique de CV.
Analyse le fichier CV joint (PDF ou image) et extrait l'ensemble des informations sous forme de JSON structuré strict.
"""


def extract_direct_gemini(cv_file_path):
    """Envoie le fichier CV directement à l'API Gemini Vision."""
    client = _get_client()
    cv_path = Path(cv_file_path)
    if not cv_path.exists():
        raise FileNotFoundError(f"Fichier CV introuvable : {cv_path}")

    file_bytes = cv_path.read_bytes()
    mime_type = _guess_mime_type(cv_path)

    models_to_try = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-2.5-pro",
        "gemini-1.5-pro",
    ]

    last_error = None
    response = None

    for model_name in models_to_try:
        try:
            print(f"[Gemini Direct] Tentative avec le modèle {model_name}...")
            response = client.models.generate_content(
                model=model_name,
                contents=[
                    types.Part.from_bytes(data=file_bytes, mime_type=mime_type),
                    PROMPT_DIRECT,
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=RESPONSE_SCHEMA,
                    temperature=0.1,
                ),
            )
            if response and response.text:
                break
        except Exception as err:
            print(f"[Gemini Direct] Échec du modèle {model_name} : {err}")
            last_error = err

    if not response or not response.text:
        raise ValueError(f"Tous les modèles Gemini ont échoué. Dernière erreur : {last_error}")

    try:
        data = json.loads(response.text)
    except (json.JSONDecodeError, TypeError) as error:
        raise ValueError(f"Réponse Gemini non-JSON : {error}")

    return data


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        res = extract_direct_gemini(sys.argv[1])
        print(json.dumps(res, indent=2, ensure_ascii=False))
