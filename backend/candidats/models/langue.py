from django.db import models
from .candidat import Candidat


class Langue(models.Model):
    candidat = models.ForeignKey(
        Candidat,
        on_delete=models.CASCADE,
        related_name="langues"
    )

    langue = models.CharField(max_length=100)
    niveau = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = "langue"

    def __str__(self):
        return f"{self.langue} - {self.candidat.nom_complet}"