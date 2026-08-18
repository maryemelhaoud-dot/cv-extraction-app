from django.db import models
from django.db.models import Q, F
from .candidat import Candidat


class Formation(models.Model):
    candidat = models.ForeignKey(
        Candidat,
        on_delete=models.CASCADE,
        related_name="formations"
    )

    diplome = models.CharField(max_length=255)
    specialite = models.CharField(max_length=255, blank=True, null=True)
    etablissement = models.CharField(max_length=255, blank=True, null=True)
    lieu = models.CharField(max_length=150, blank=True, null=True)
    periode = models.CharField(max_length=100, blank=True, null=True)
    date_debut = models.DateField(blank=True, null=True)
    date_fin = models.DateField(blank=True, null=True)
    en_cours = models.BooleanField(default=False)
    niveau = models.CharField(max_length=100, blank=True, null=True)
    mention = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "formation"
        constraints = [
            models.CheckConstraint(
                check=(
                    Q(date_fin__isnull=True)
                    | Q(date_debut__isnull=True)
                    | Q(date_fin__gte=F("date_debut"))
                ),
                name="formation_date_fin_apres_date_debut",
            )
        ]

    def __str__(self):
        return f"{self.diplome} - {self.candidat.nom_complet}"