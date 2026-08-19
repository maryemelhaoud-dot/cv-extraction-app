"""Extraction et structuration de CV via DeepSeek API."""

import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"

SYSTEM_PROMPT = """Tu es un expert en extraction et structuration de CV.
Tu reçois un texte brut de CV extrait intégralement par OCR (PaddleOCR).
Analyse le texte et génère un objet JSON structuré strict correspondant exactement à cette structure :

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
  "certifications": [
    {
      "nom": "Nom de la certification",
      "organisme": "Organisme émetteur ou null",
      "date_obtention": null,
      "date_expiration": null,
      "url_verification": null
    }
  ],
  "projets": [
    {
      "nom_projet": "Nom du projet",
      "type_projet": "académique, personnel ou professionnel, ou null",
      "technologies": "Technologies utilisées, séparées par des virgules, ou null",
      "url_projet": null,
      "periode": "dates telles quelles ou null",
      "date_debut": null,
      "date_fin": null,
      "en_cours": false,
      "description": "description du projet ou null",
      "role": "rôle du candidat dans le projet ou null"
    }
  ],
  "centres_interet": [
    {
      "intitule": "Nom du centre d'intérêt",
      "categorie": null,
      "description": null
    }
  ]
}

Règles :
- Les tableaux ci-dessus contiennent UN exemple de structure par section, pour te montrer les noms de champs exacts à utiliser. Ce ne sont pas des valeurs à copier : si une section n'a aucune information dans le CV, retourne un tableau vide [] pour cette clé.
- Réponds UNIQUEMENT avec l'objet JSON valide, sans texte d'introduction ni balises markdown.
- N'invente pas d'informations non présentes dans le texte OCR.
"""


def structure_cv_deepseek(ocr_text):
    """Envoie le texte OCR à l'API DeepSeek pour structuration JSON."""
    if not DEEPSEEK_API_KEY:
        raise RuntimeError("DEEPSEEK_API_KEY manquant dans le fichier .env de ocr-service")

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Voici le texte OCR du CV à structurer :\n\n{ocr_text}"}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.1,
    }

    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        if err.response is not None and err.response.status_code == 402:
            raise RuntimeError("Erreur API DeepSeek (402 Payment Required) : Solde de compte insuffisant. Veuillez recharger votre solde DeepSeek API.") from err
        raise RuntimeError(f"Erreur API DeepSeek ({err.response.status_code if err.response is not None else 'HTTPError'}) : {err}") from err
    except requests.exceptions.RequestException as err:
        raise RuntimeError(f"Erreur de connexion à l'API DeepSeek : {err}") from err

    result_json = response.json()
    content = result_json["choices"][0]["message"]["content"].strip()

    if content.startswith("```json"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]

    data = json.loads(content.strip())
    return data


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        res = structure_cv_deepseek(sys.argv[1])
        print(json.dumps(res, indent=2, ensure_ascii=False))