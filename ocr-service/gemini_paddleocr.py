"""Extraction et structuration de CV via Gemini + PaddleOCR."""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

def _get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY manquant dans le fichier .env")
    return genai.Client(api_key=api_key)

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "candidat": {
            "type": "object",
            "properties": {
                "nom_complet": {"type": "string"},
                "titre_profil": {"type": "string", "nullable": True},
                "email": {"type": "string", "nullable": True},
                "telephone": {"type": "string", "nullable": True},
                "telephone_secondaire": {"type": "string", "nullable": True},
                "adresse": {"type": "string", "nullable": True},
                "ville": {"type": "string", "nullable": True},
                "code_postal": {"type": "string", "nullable": True},
                "pays": {"type": "string", "nullable": True},
                "linkedin": {"type": "string", "nullable": True},
                "portfolio": {"type": "string", "nullable": True},
                "site_web": {"type": "string", "nullable": True},
                "date_naissance": {"type": "string", "nullable": True, "description": "format YYYY-MM-DD"},
                "lieu_naissance": {"type": "string", "nullable": True},
                "nationalite": {"type": "string", "nullable": True},
                "situation_familiale": {"type": "string", "nullable": True},
                "permis_conduire": {"type": "string", "nullable": True},
                "mobilite_geographique": {"type": "string", "nullable": True},
                "disponibilite": {"type": "string", "nullable": True},
                "resume_profil": {"type": "string", "nullable": True},
                "objectif_professionnel": {"type": "string", "nullable": True},
            },
            "required": ["nom_complet"],
        },
        "formations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "diplome": {"type": "string"},
                    "specialite": {"type": "string", "nullable": True},
                    "etablissement": {"type": "string", "nullable": True},
                    "lieu": {"type": "string", "nullable": True},
                    "periode": {"type": "string", "nullable": True, "description": "texte tel qu'écrit sur le CV, ex: '2023-2025'"},
                    "date_debut": {"type": "string", "nullable": True, "description": "YYYY-MM-DD si déductible, sinon null"},
                    "date_fin": {"type": "string", "nullable": True},
                    "en_cours": {"type": "boolean"},
                    "niveau": {"type": "string", "nullable": True},
                    "mention": {"type": "string", "nullable": True},
                    "description": {"type": "string", "nullable": True},
                },
                "required": ["diplome"],
            },
        },
        "experiences": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "nullable": True, "description": "ex: stage, emploi, bénévolat, leadership associatif"},
                    "poste": {"type": "string"},
                    "organisme": {"type": "string", "nullable": True},
                    "lieu": {"type": "string", "nullable": True},
                    "periode": {"type": "string", "nullable": True},
                    "date_debut": {"type": "string", "nullable": True},
                    "date_fin": {"type": "string", "nullable": True},
                    "en_cours": {"type": "boolean"},
                    "description": {"type": "string", "nullable": True},
                },
                "required": ["poste"],
            },
        },
        "competences": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "nom_competence": {"type": "string"},
                    "categorie": {"type": "string", "nullable": True, "description": "ex: Technique, Personnelle, Outils"},
                    "sous_categorie": {"type": "string", "nullable": True, "description": "ex: Langages de programmation, Front-end, Back-end"},
                    "niveau": {"type": "string", "nullable": True},
                    "annees_experience": {"type": "number", "nullable": True},
                },
                "required": ["nom_competence"],
            },
        },
        "langues": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "langue": {"type": "string"},
                    "niveau": {"type": "string", "nullable": True},
                },
                "required": ["langue"],
            },
        },
        "certifications": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "nom": {"type": "string"},
                    "organisme": {"type": "string", "nullable": True},
                    "date_obtention": {"type": "string", "nullable": True},
                    "date_expiration": {"type": "string", "nullable": True},
                    "url_verification": {"type": "string", "nullable": True},
                },
                "required": ["nom"],
            },
        },
        "projets": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "nom_projet": {"type": "string"},
                    "type_projet": {"type": "string", "nullable": True, "description": "ex: académique, personnel, professionnel"},
                    "technologies": {"type": "string", "nullable": True, "description": "liste de technologies séparées par des virgules"},
                    "url_projet": {"type": "string", "nullable": True},
                    "periode": {"type": "string", "nullable": True},
                    "date_debut": {"type": "string", "nullable": True},
                    "date_fin": {"type": "string", "nullable": True},
                    "en_cours": {"type": "boolean"},
                    "description": {"type": "string", "nullable": True},
                    "role": {"type": "string", "nullable": True},
                },
                "required": ["nom_projet"],
            },
        },
        "centres_interet": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "intitule": {"type": "string"},
                    "categorie": {"type": "string", "nullable": True},
                    "description": {"type": "string", "nullable": True},
                },
                "required": ["intitule"],
            },
        },
    },
    "required": ["candidat", "formations", "experiences", "competences", "langues", "certifications", "projets", "centres_interet"],
}


PROMPT = """Tu es un extracteur de données de CV. Analyse ce CV (le fichier joint fait foi pour la mise en page et le contenu exact) et produis un JSON structuré.

Un texte brut extrait par OCR est fourni ci-dessous en complément -- utilise-le comme AIDE si une partie du fichier est difficile à lire, mais fais confiance au FICHIER en priorité en cas de désaccord entre les deux sources, car le fichier est la référence exacte.

Règles :
- N'invente AUCUNE information qui n'est pas dans le CV. Si une donnée est absente, mets null (ou liste vide pour les sections absentes).
- Les dates : mets-les au format YYYY-MM-DD uniquement si tu peux les déduire avec certitude (ex: "Mars 2022" -> "2022-03-01" avec le jour à 01 par convention). Sinon, laisse date_debut/date_fin à null et garde le texte original dans "periode".
- "en_cours" = true si le CV indique explicitement que c'est en cours (ex: "Aujourd'hui", "present", "en cours").
- Sépare bien chaque formation/expérience/projet en une entrée distincte, dans l'ordre où ils apparaissent sur le CV (généralement du plus récent au plus ancien).
- Les compétences techniques et personnelles vont dans "competences" (avec "categorie" pour les distinguer), pas dans "centres_interet".

--- TEXTE OCR (aide, peut contenir des erreurs) ---
{ocr_text}
--- FIN TEXTE OCR ---
"""


def _guess_mime_type(file_path):
    ext = Path(file_path).suffix.lower()
    return {
        ".pdf": "application/pdf",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
    }.get(ext, "application/octet-stream")


def structure_cv(ocr_text, cv_file_path, provider="gemini", **kwargs):
    """
    Envoie le texte OCR + le fichier CV brut à Gemini, et retourne un dict
    Python structuré avec les clés exactes attendues par le backend Django.

    Paramètres :
        ocr_text (str)      : texte extrait par PaddleOCR (peut être imparfait)
        cv_file_path (str)  : chemin vers le fichier CV original (PDF/image)

    Retour :
        dict avec les clés : candidat, formations, experiences, competences,
        langues, certifications, projets, centres_interet
    """
    cv_file_path = Path(cv_file_path)
    if not cv_file_path.exists():
        raise FileNotFoundError(f"Fichier CV introuvable : {cv_file_path}")

    client = _get_client()
    file_bytes = cv_file_path.read_bytes()
    mime_type = _guess_mime_type(cv_file_path)

    prompt = PROMPT.format(ocr_text=ocr_text or "(aucun texte OCR disponible)")

    models_to_try = [
        "gemini-3.6-flash",
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
            print(f"[Gemini Structuring] Tentative avec le modèle {model_name}...")
            response = client.models.generate_content(
                model=model_name,
                contents=[
                    types.Part.from_bytes(data=file_bytes, mime_type=mime_type),
                    prompt,
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
            print(f"[Gemini Structuring] Échec du modèle {model_name} : {err}")
            last_error = err

    if not response or not response.text:
        raise ValueError(f"Tous les modèles Gemini ont échoué. Dernière erreur : {last_error}")

    try:
        data = json.loads(response.text)
    except (json.JSONDecodeError, TypeError) as error:
        raise ValueError(
            f"Réponse Gemini non-JSON ou vide : {error}\nRéponse brute : {getattr(response, 'text', response)}"
        )

    return data


PROMPT_TEXT_ONLY = """Tu es un expert en extraction et structuration de données de CV.
Voici le texte brut d'un CV, extrait intégralement par OCR (PaddleOCR) de l'en-tête jusqu'au pied de page, ordonné par sections, colonnes et lignes.

Analyse ce texte et génère un JSON structuré exact correspondant aux champs demandés.

Règles :
- Reconstruis l'identité complète du candidat (nom_complet, titre_profil, email, telephone, adresse, ville, etc.).
- Extrais fidèlement chaque formation, expérience, compétence, langue, certification, projet et centre d'intérêt.
- N'invente AUCUNE information qui n'est pas dans le texte OCR. Mets null pour les champs absents.
- Sépare bien chaque formation/expérience/projet en une entrée distincte.

--- TEXTE OCR DU CV ---
{ocr_text}
--- FIN TEXTE OCR ---
"""


def structure_cv_from_text_only(ocr_text):
    """
    Envoie UNIQUEMENT le texte OCR extrait par PaddleOCR à Gemini (SANS joindre le fichier PDF/image).
    Permet de tester et d'évaluer la précision d'extraction de PaddleOCR à 100%.
    """
    client = _get_client()
    prompt = PROMPT_TEXT_ONLY.format(ocr_text=ocr_text or "(aucun texte OCR extrait)")

    models_to_try = [
        "gemini-3.6-flash",
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
            print(f"[Gemini Texte-Seul] Tentative avec le modèle {model_name}...")
            response = client.models.generate_content(
                model=model_name,
                contents=[prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=RESPONSE_SCHEMA,
                    temperature=0.1,
                ),
            )
            if response and response.text:
                break
        except Exception as err:
            print(f"[Gemini Texte-Seul] Échec du modèle {model_name} : {err}")
            last_error = err

    if not response or not response.text:
        raise ValueError(f"Tous les modèles Gemini ont échoué en mode Texte-Seul. Dernière erreur : {last_error}")

    try:
        data = json.loads(response.text)
    except (json.JSONDecodeError, TypeError) as error:
        raise ValueError(
            f"Réponse Gemini non-JSON : {error}\nRéponse brute : {getattr(response, 'text', response)}"
        )

    return data


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage : python gemini_structuring.py chemin/vers/cv.pdf [chemin/vers/texte_ocr.txt]")
        sys.exit(1)

    cv_path = sys.argv[1]
    ocr_text_path = sys.argv[2] if len(sys.argv) > 2 else None

    ocr_text = Path(ocr_text_path).read_text(encoding="utf-8") if ocr_text_path else ""

    print("Envoi à Gemini...")
    result = structure_cv(ocr_text, cv_path)

    print(json.dumps(result, indent=2, ensure_ascii=False))