from rest_framework import serializers
from .models import (
    Candidat, Formation, Experience, Competence,
    Langue, Certification, Projet, CentreInteret,
)


class FormationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Formation
        fields = '__all__'


class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = '__all__'


class CompetenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competence
        fields = '__all__'


class LangueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Langue
        fields = '__all__'


class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = '__all__'


class ProjetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projet
        fields = '__all__'


class CentreInteretSerializer(serializers.ModelSerializer):
    class Meta:
        model = CentreInteret
        fields = '__all__'


class CandidatSerializer(serializers.ModelSerializer):
    formations = FormationSerializer(many=True, read_only=True)
    experiences = ExperienceSerializer(many=True, read_only=True)
    competences = CompetenceSerializer(many=True, read_only=True)
    langues = LangueSerializer(many=True, read_only=True)
    certifications = CertificationSerializer(many=True, read_only=True)
    projets = ProjetSerializer(many=True, read_only=True)
    centres_interet = CentreInteretSerializer(many=True, read_only=True)

    class Meta:
        model = Candidat
        fields = '__all__'