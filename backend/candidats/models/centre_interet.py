from django.db import models
from .candidat import Candidat


class CentreInteret(models.Model):
    candidat = models.ForeignKey(
        Candidat,
        on_delete=models.CASCADE,
        related_name="centres_interet"
    )

    intitule = models.CharField(max_length=255)
    categorie = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "centre_interet"

    def __str__(self):
        return f"{self.intitule} - {self.candidat.nom_complet}"