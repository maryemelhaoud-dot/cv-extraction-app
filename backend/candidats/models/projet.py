from django.db import models
from django.db.models import Q, F
from .candidat import Candidat


class Projet(models.Model):
    candidat = models.ForeignKey(
        Candidat,
        on_delete=models.CASCADE,
        related_name="projets"
    )

    nom_projet = models.TextField()
    type_projet = models.CharField(max_length=100, blank=True, null=True)
    technologies = models.TextField(blank=True, null=True)
    url_projet = models.URLField(max_length=500, blank=True, null=True)
    periode = models.CharField(max_length=100, blank=True, null=True)
    date_debut = models.DateField(blank=True, null=True)
    date_fin = models.DateField(blank=True, null=True)
    en_cours = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)
    role = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        db_table = "projet"
        constraints = [
            models.CheckConstraint(
                check=(
                    Q(date_fin__isnull=True)
                    | Q(date_debut__isnull=True)
                    | Q(date_fin__gte=F("date_debut"))
                ),
                name="projet_date_fin_apres_date_debut",)]