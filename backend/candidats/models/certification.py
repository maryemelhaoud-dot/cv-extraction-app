from django.db import models
from .candidat import Candidat


class Certification(models.Model):
    candidat = models.ForeignKey(
        Candidat,
        on_delete=models.CASCADE,
        related_name="certifications"
    )

    nom = models.CharField(max_length=255)
    organisme = models.CharField(max_length=255, blank=True, null=True)
    date_obtention = models.DateField(blank=True, null=True)
    date_expiration = models.DateField(blank=True, null=True)
    url_verification = models.URLField(max_length=500, blank=True, null=True)

    class Meta:
        db_table = "certification"

    def __str__(self):
        return f"{self.nom} - {self.candidat.nom_complet}"