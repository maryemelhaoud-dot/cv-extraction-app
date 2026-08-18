from django.db import models
from .candidat import Candidat


class Competence(models.Model):
    candidat = models.ForeignKey(
        Candidat,
        on_delete=models.CASCADE,
        related_name="competences"
    )

    nom_competence = models.CharField(max_length=255)
    categorie = models.CharField(max_length=100, blank=True, null=True)
    sous_categorie = models.CharField(max_length=100, blank=True, null=True)
    niveau = models.CharField(max_length=100, blank=True, null=True)
    annees_experience = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        blank=True,
        null=True
    )

    class Meta:
        db_table = "competence"

    def __str__(self):
        return f"{self.nom_competence} - {self.candidat.nom_complet}"