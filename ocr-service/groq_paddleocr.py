"""Extraction et structuration de CV via Groq API."""

import json
import os
import re
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "openai/gpt-oss-120b"

SYSTEM_PROMPT = """Tu es un expert en extraction et structuration de CV.
Tu reçois un texte brut de CV extrait intégralement par OCR (PaddleOCR).
Analyse le texte et génère un objet json structuré strict correspondant exactement à cette structure :

{
  "candidat": {
    "nom_complet": "Nom et prénom du candidat",
    "titre_profil": "intitulé du poste ou profil",
    "email": "adresse email ou null",
    "telephone": "numéro principal ou null",
    "telephone_secondaire": null,
    "adresse": null,
    "ville": "ville ou null",
    "code_postal": null,
    "pays": "Maroc",
    "linkedin": null,
    "portfolio": null,
    "site_web": null,
    "date_naissance": null,
    "lieu_naissance": null,
    "nationalite": null,
    "situation_familiale": null,
    "permis_conduire": null,
    "mobilite_geographique": null,
    "disponibilite": null,
    "resume_profil": "résumé ou présentation du candidat",
    "objectif_professionnel": null
  },
  "formations": [
    {
      "diplome": "nom du diplôme",
      "specialite": null,
      "etablissement": "école ou université",
      "lieu": null,
      "periode": "dates telles quelles (ex: 2020-2023)",
      "date_debut": null,
      "date_fin": null,
      "en_cours": false,
      "niveau": null,
      "mention": null,
      "description": null
    }
  ],
  "experiences": [
    {
      "poste": "intitulé du poste",
      "type": null,
      "organisme": "entreprise ou organisation",
      "lieu": null,
      "periode": "ex: 2022 - 2023",
      "date_debut": null,
      "date_fin": null,
      "en_cours": false,
      "description": "détail des tâches"
    }
  ],
  "competences": [
    {
      "nom_competence": "Nom de la compétence",
      "categorie": "Technique",
      "sous_categorie": null,
      "niveau": null,
      "annees_experience": null
    }
  ],
  "langues": [
    {
      "langue": "Langue (ex: Français, Anglais)",
      "niveau": "Niveau (ex: Courant, B2)"
    }
  ],
  "certifications": [],
  "projets": [],
  "centres_interet": []
}

Règles :
- Réponds UNIQUEMENT avec l'objet json valide, sans texte d'introduction ni balises markdown.
- N'invente pas d'informations non présentes dans le texte OCR.
"""


def _clean_json_content(content: str) -> str:
    content = content.strip()
    if content.startswith("```json"):
        content = content[7:]
    elif content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()

    json_match = re.search(r"(\{.*\})", content, re.DOTALL)
    if json_match:
        content = json_match.group(1)

    return content


def _parse_json_robustly(content: str) -> dict:
    cleaned = _clean_json_content(content)

    # 1. Tentative directe
    try:
        return json.loads(cleaned, strict=False)
    except Exception:
        pass

    # 2. Nettoyage des virgules traînantes (trailing commas)
    cleaned_fixed = re.sub(r",\s*([}\]])", r"\1", cleaned)
    try:
        return json.loads(cleaned_fixed, strict=False)
    except Exception:
        pass

    # 3. Réparation des chaînes et balises tronquées
    repaired = cleaned_fixed.rstrip()
    if repaired.endswith(","):
        repaired = repaired[:-1]

    num_quotes = len(re.findall(r'(?<!\\)"', repaired))
    if num_quotes % 2 != 0:
        repaired += '"'

    open_braces = repaired.count("{") - repaired.count("}")
    open_brackets = repaired.count("[") - repaired.count("]")
    repaired += "]" * max(0, open_brackets) + "}" * max(0, open_braces)

    try:
        return json.loads(repaired, strict=False)
    except Exception:
        pass

    # 4. Nettoyage des caractères de contrôle invalides
    cleaned_ultimate = re.sub(r"[\x00-\x1f\x7f-\x9f]", " ", repaired)
    try:
        return json.loads(cleaned_ultimate, strict=False)
    except Exception as err:
        raise ValueError(f"Erreur de décodage JSON : {err}") from err


def structure_cv_groq(ocr_text):
    """Envoie le texte OCR à l'API Groq pour structuration JSON."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY manquant dans le fichier .env de ocr-service")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    models_to_try = [
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
        "qwen/qwen3.6-27b",
    ]

    last_error = None
    content = None

    for model_name in models_to_try:
        payload = {
            "model": model_name,
            "max_tokens": 4096,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Voici le texte OCR du CV à structurer en json :\n\n{ocr_text}"}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.1,
        }

        print(f"[Groq Structuring] Tentative avec le modèle {model_name}...")
        try:
            response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            result_json = response.json()
            content = result_json["choices"][0]["message"]["content"]
            if content:
                break
        except Exception as err:
            print(f"[Groq Structuring] Échec du modèle {model_name} : {err}")
            last_error = err

    if not content:
        raise RuntimeError(f"Tous les modèles Groq ont échoué. Dernière erreur : {last_error}")

    try:
        data = _parse_json_robustly(content)
    except Exception as err:
        raise RuntimeError(f"Erreur de décodage JSON Groq : {err}") from err

    return data


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        res = structure_cv_groq(sys.argv[1])
        print(json.dumps(res, indent=2, ensure_ascii=False))