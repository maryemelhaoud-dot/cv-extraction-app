from datetime import date

import requests
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from .models import (
    Candidat, Formation, Experience, Competence,
    Langue, Certification, Projet, CentreInteret,
)
from .serializers import (
    CandidatSerializer, FormationSerializer, ExperienceSerializer,
    CompetenceSerializer, LangueSerializer, CertificationSerializer,
    ProjetSerializer, CentreInteretSerializer,
)

import os
import mimetypes
import threading

OCR_SERVICE_URL = os.getenv("OCR_SERVICE_URL", "http://127.0.0.1:8001/extract")
OCR_SERVICE_TIMEOUT = 600


class CandidatViewSet(viewsets.ModelViewSet):
    queryset = Candidat.objects.all()
    serializer_class = CandidatSerializer


class FormationViewSet(viewsets.ModelViewSet):
    queryset = Formation.objects.all()
    serializer_class = FormationSerializer


class ExperienceViewSet(viewsets.ModelViewSet):
    queryset = Experience.objects.all()
    serializer_class = ExperienceSerializer


class CompetenceViewSet(viewsets.ModelViewSet):
    queryset = Competence.objects.all()
    serializer_class = CompetenceSerializer


class LangueViewSet(viewsets.ModelViewSet):
    queryset = Langue.objects.all()
    serializer_class = LangueSerializer


class CertificationViewSet(viewsets.ModelViewSet):
    queryset = Certification.objects.all()
    serializer_class = CertificationSerializer


class ProjetViewSet(viewsets.ModelViewSet):
    queryset = Projet.objects.all()
    serializer_class = ProjetSerializer


class CentreInteretViewSet(viewsets.ModelViewSet):
    queryset = CentreInteret.objects.all()
    serializer_class = CentreInteretSerializer


def _parse_date(value):
    """Convertit une date 'YYYY-MM-DD' (ou None/vide) en objet date Django."""
    if not value:
        return None
    try:
        return date.fromisoformat(str(value).strip())
    except (ValueError, TypeError):
        return None


def _traiter_cv_background(candidat_id, provider):
    try:
        candidat = Candidat.objects.get(id=candidat_id)
        if not candidat.fichier_cv or not hasattr(candidat.fichier_cv, 'path') or not candidat.fichier_cv.path:
            print(f"CV {candidat_id} : Fichier non trouvé sur le disque.")
            candidat.statut_traitement = "erreur"
            candidat.save()
            return

        filename = os.path.basename(candidat.fichier_cv.name)
        mime_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"

        with open(candidat.fichier_cv.path, "rb") as f:
            file_bytes = f.read()

        files_payload = {"file": (filename, file_bytes, mime_type)}
        print(f"Appel du service OCR {OCR_SERVICE_URL} pour candidat ID {candidat_id}...")

        response = requests.post(
            OCR_SERVICE_URL,
            files=files_payload,
            params={"provider": provider},
            timeout=OCR_SERVICE_TIMEOUT,
        )

        if response.status_code != 200:
            print(f"Erreur HTTP OCR ({response.status_code}): {response.text}")
            candidat.statut_traitement = "erreur"
            candidat.resume_profil = f"Erreur OCR ({response.status_code}): {response.text}"
            candidat.save()
            return

        data = response.json()
        print(f"Extraction réussie pour candidat ID {candidat_id}.")
        enregistrer_donnees_candidat(candidat, data)

    except Exception as error:
        print(f"Erreur lors du traitement arrière-plan CV {candidat_id} : {error}")
        try:
            candidat = Candidat.objects.get(id=candidat_id)
            candidat.statut_traitement = "erreur"
            candidat.resume_profil = str(error)
            candidat.save()
        except Exception as e:
            print(f"Impossible de sauvegarder le statut d'erreur : {e}")


class UploadCVView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        # Accepte le fichier sous plusieurs noms possibles ('fichier_cv', 'file', 'cv')
        fichier = (
            request.FILES.get("fichier_cv") 
            or request.FILES.get("file") 
            or request.FILES.get("cv")
        )
        provider = request.data.get("provider", "gemini")

        if not fichier:
            return Response(
                {"erreur": "Aucun fichier reçu. Vérifiez la clé envoyée dans le FormData."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Création initiale du candidat
        candidat = Candidat.objects.create(
            nom_complet="En cours de traitement",
            fichier_cv=fichier,
            statut_traitement="en_cours",
            source_cv="upload",
        )

        # Lancer le traitement OCR/IA en arrière-plan sans bloquer la requête
        threading.Thread(
            target=_traiter_cv_background,
            args=(candidat.id, provider),
            daemon=True
        ).start()

        serializer = CandidatSerializer(candidat)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


def enregistrer_donnees_candidat(candidat, data):
    """Met à jour le Candidat et crée les objets liés à partir du JSON renvoyé par l'ocr-service."""

    infos = data.get("candidat", {})
    for champ in (
        "nom_complet", "titre_profil", "email", "telephone", "telephone_secondaire",
        "adresse", "ville", "code_postal", "pays", "linkedin", "portfolio", "site_web",
        "lieu_naissance", "nationalite", "situation_familiale", "permis_conduire",
        "mobilite_geographique", "disponibilite", "resume_profil", "objectif_professionnel",
    ):
        valeur = infos.get(champ)
        if valeur:
            setattr(candidat, champ, valeur)

    date_naissance = _parse_date(infos.get("date_naissance"))
    if date_naissance:
        candidat.date_naissance = date_naissance

    candidat.statut_traitement = "traité"
    candidat.save()

    # Suppression des anciennes sous-entités pour ré-enregistrement propre
    candidat.formations.all().delete()
    candidat.experiences.all().delete()
    candidat.competences.all().delete()
    candidat.langues.all().delete()
    candidat.certifications.all().delete()
    candidat.projets.all().delete()
    candidat.centres_interet.all().delete()

    Formation.objects.bulk_create([
        Formation(
            candidat=candidat,
            diplome=f.get("diplome") or "",
            specialite=f.get("specialite"),
            etablissement=f.get("etablissement"),
            lieu=f.get("lieu"),
            periode=f.get("periode"),
            date_debut=_parse_date(f.get("date_debut")),
            date_fin=_parse_date(f.get("date_fin")),
            en_cours=bool(f.get("en_cours")),
            niveau=f.get("niveau"),
            mention=f.get("mention"),
            description=f.get("description"),
        )
        for f in data.get("formations", []) if f.get("diplome")
    ])

    Experience.objects.bulk_create([
        Experience(
            candidat=candidat,
            type=e.get("type"),
            poste=e.get("poste") or "",
            organisme=e.get("organisme"),
            lieu=e.get("lieu"),
            periode=e.get("periode"),
            date_debut=_parse_date(e.get("date_debut")),
            date_fin=_parse_date(e.get("date_fin")),
            en_cours=bool(e.get("en_cours")),
            description=e.get("description"),
        )
        for e in data.get("experiences", []) if e.get("poste")
    ])

    Competence.objects.bulk_create([
        Competence(
            candidat=candidat,
            nom_competence=c.get("nom_competence") or "",
            categorie=c.get("categorie"),
            sous_categorie=c.get("sous_categorie"),
            niveau=c.get("niveau"),
            annees_experience=c.get("annees_experience"),
        )
        for c in data.get("competences", []) if c.get("nom_competence")
    ])

    Langue.objects.bulk_create([
        Langue(candidat=candidat, langue=l.get("langue") or "", niveau=l.get("niveau"))
        for l in data.get("langues", []) if l.get("langue")
    ])

    Certification.objects.bulk_create([
        Certification(
            candidat=candidat,
            nom=c.get("nom") or "",
            organisme=c.get("organisme"),
            date_obtention=_parse_date(c.get("date_obtention")),
            date_expiration=_parse_date(c.get("date_expiration")),
            url_verification=c.get("url_verification"),
        )
        for c in data.get("certifications", []) if c.get("nom")
    ])

    Projet.objects.bulk_create([
        Projet(
            candidat=candidat,
            nom_projet=p.get("nom_projet") or "",
            type_projet=p.get("type_projet"),
            technologies=p.get("technologies"),
            url_projet=p.get("url_projet"),
            periode=p.get("periode"),
            date_debut=_parse_date(p.get("date_debut")),
            date_fin=_parse_date(p.get("date_fin")),
            en_cours=bool(p.get("en_cours")),
            description=p.get("description"),
            role=p.get("role"),
        )
        for p in data.get("projets", []) if p.get("nom_projet")
    ])

    CentreInteret.objects.bulk_create([
        CentreInteret(
            candidat=candidat,
            intitule=ci.get("intitule") or "",
            categorie=ci.get("categorie"),
            description=ci.get("description"),
        )
        for ci in data.get("centres_interet", []) if ci.get("intitule")
    ])