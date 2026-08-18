from django.db import models
from django.db.models import Q, F
from .candidat import Candidat


class Experience(models.Model):
    candidat = models.ForeignKey(
        Candidat,
        on_delete=models.CASCADE,
        related_name="experiences"
    )

    type = models.CharField(max_length=100, blank=True, null=True)
    poste = models.CharField(max_length=255)
    organisme = models.CharField(max_length=255, blank=True, null=True)
    lieu = models.CharField(max_length=150, blank=True, null=True)
    periode = models.CharField(max_length=100, blank=True, null=True)
    date_debut = models.DateField(blank=True, null=True)
    date_fin = models.DateField(blank=True, null=True)
    en_cours = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "experience"
        constraints = [
            models.CheckConstraint(
                check=(
                    Q(date_fin__isnull=True)
                    | Q(date_debut__isnull=True)
                    | Q(date_fin__gte=F("date_debut"))
                ),
                name="experience_date_fin_apres_date_debut",
            )
        ]

    def __str__(self):
        return f"{self.poste} - {self.candidat.nom_complet}"