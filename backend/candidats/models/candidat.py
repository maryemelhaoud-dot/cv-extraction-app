from django.db import models


class Candidat(models.Model):

    STATUT_CHOICES = [
        ("en_cours", "En cours"),
        ("traité", "Traité"),
        ("erreur", "Erreur"),
    ]

    # Identité
    nom_complet = models.CharField(max_length=255)
    titre_profil = models.CharField(max_length=255, blank=True, null=True)

    # Contact
    email = models.EmailField(blank=True, null=True)
    telephone = models.CharField(max_length=30, blank=True, null=True)
    telephone_secondaire = models.CharField(max_length=30, blank=True, null=True)

    # Adresse complète
    adresse = models.TextField(blank=True, null=True)
    ville = models.CharField(max_length=100, blank=True, null=True)
    code_postal = models.CharField(max_length=20, blank=True, null=True)
    pays = models.CharField(max_length=100, default="Maroc", blank=True)

    # Liens professionnels
    linkedin = models.URLField(max_length=500, blank=True, null=True)
    portfolio = models.URLField(max_length=500, blank=True, null=True)
    site_web = models.URLField(max_length=500, blank=True, null=True)

    # Informations personnelles
    date_naissance = models.DateField(blank=True, null=True)
    lieu_naissance = models.CharField(max_length=150, blank=True, null=True)
    nationalite = models.CharField(max_length=100, blank=True, null=True)
    situation_familiale = models.CharField(max_length=100, blank=True, null=True)

    # Mobilité & disponibilité
    permis_conduire = models.CharField(max_length=100, blank=True, null=True)
    mobilite_geographique = models.CharField(max_length=100, blank=True, null=True)
    disponibilite = models.CharField(max_length=100, blank=True, null=True)

    # Profil
    resume_profil = models.TextField(blank=True, null=True)
    objectif_professionnel = models.TextField(blank=True, null=True)

    # Photo & fichier
    photo = models.ImageField(upload_to="photos/", blank=True, null=True)
    fichier_cv = models.FileField(upload_to="cv/")

    # Métadonnées
    date_upload = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    source_cv = models.CharField(max_length=50, default="upload")
    statut_traitement = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default="en_cours"
    )

    class Meta:
        db_table = "candidat"
        ordering = ["-date_upload"]

    def __str__(self):
        return self.nom_complet