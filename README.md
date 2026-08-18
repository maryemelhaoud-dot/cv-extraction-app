# Application d'Extraction et de Structuration de CV (CV Extraction App)

Une application complète et moderne pour l'extraction de texte à partir de CV (PDF, PNG, JPG) grâce à **PaddleOCR** et la structuration intelligente en JSON via **Groq (Llama 3)**, **Gemini Vision**, ou **DeepSeek**, la persistance REST dans un backend **Django**, et une interface utilisateur en **React (Vite)**.

---

##  Architecture du Projet

```
cv-extraction-app/
├── ocr-service/             # Microservice FastAPI (PaddleOCR + LLMs)
│   ├── app.py               # API FastAPI avec endpoint /extract
│   ├── paddle_extraction.py # Moteur d'extraction OCR (PaddleOCR)
│   ├── groq_paddleocr.py    # Integration Groq (Llama 3 / Compound)
│   ├── gemini_direct.py     # Integration Gemini Vision Direct
│   ├── gemini_paddleocr.py  # Integration Gemini Text-Only
│   ├── deepseek_paddleocr.py# Integration DeepSeek API
│   ├── .env.example         # Modèle des variables d'environnement
│   ├── Dockerfile
│   └── requirements.txt
│
├── backend/                 # Backend Django REST Framework
│   ├── candidats/           # Modèles Django (Candidat, Expériences, Formations...)
│   │   ├── models/          # Schéma ORM relationnel
│   │   └── views.py         # API Endpoint Upload & CRUD candidats
│   ├── config/              # Configuration Django
│   ├── .env.example         # Modèle des variables d'environnement
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                # Application Frontend React (Vite)
│   ├── src/                 # Composants UI & Services
│   ├── Dockerfile
│   └── package.json
│
└── docker-compose.yml       # Orchestration Docker (PostgreSQL, OCR, Backend, Frontend)
```

---

##  Méthodes d'Extraction Supportées

L'utilisateur peut choisir sa méthode d'extraction préférée depuis l'interface web :
1. **Gemini Vision Direct** : Envoi du document directement à Gemini Vision sans étape OCR.
2. **PaddleOCR + Groq Llama 3 (Gratuit)** : Extraction OCR locale + structuration sémantique  via Groq API.
3. **PaddleOCR + Gemini** : Extraction OCR locale + structuration sémantique via Gemini.
4. **PaddleOCR + DeepSeek** : Extraction OCR locale + structuration via DeepSeek.

---

## 🚀 Démarrage Rapide

### 📥 1. Clonage du Dépôt

```bash
git clone https://github.com/maryemelhaoud-dot/cv-extraction-app.git
cd cv-extraction-app
```

---

### Option 1 : Avec Docker Compose (Recommandé)

1. Assurez-vous d'avoir des fichiers `.env` valides dans `ocr-service/` et `backend/` (copiez depuis `.env.example`).
2. Lancez les conteneurs :
   ```bash
   docker compose up --build
   ```

Services accessibles :
- **Frontend React** : `http://localhost:5173`
- **Backend Django** : `http://localhost:8000/api/`
- **OCR Service FastAPI** : `http://localhost:8001/docs` (Swagger UI)
- **Base de données PostgreSQL** : `localhost:5432`

---

### Option 2 : Lancement Manuel (Développement Local)

#### 1. Configuration des Environnements (`.env`)
- Dans `ocr-service/`, copiez `.env.example` en `.env` et renseignez vos clés d'API (`GROQ_API_KEY`, `GEMINI_API_KEY`, etc.).
- Dans `backend/`, copiez `.env.example` en `.env` et configurez vos identifiants PostgreSQL.

#### 2. Lancer le Microservice OCR (`ocr-service`)
```bash
cd ocr-service
python -m venv venv
.\venv\Scripts\Activate.ps1   # Sur Windows PowerShell
pip install -r requirements.txt
python app.py
```
*Accessible sur `http://127.0.0.1:8001`.*

#### 3. Lancer le Backend Django (`backend`)
```bash
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
*Accessible sur `http://127.0.0.1:8000`.*

#### 4. Lancer le Frontend React (`frontend`)
```bash
cd frontend
npm install
npm run dev
```
*Accessible sur `http://localhost:5173`.*

---
