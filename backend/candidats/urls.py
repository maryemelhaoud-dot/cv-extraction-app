from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    CandidatViewSet, FormationViewSet, ExperienceViewSet,
    CompetenceViewSet, LangueViewSet, CertificationViewSet,
    ProjetViewSet, CentreInteretViewSet, UploadCVView,
)

router = DefaultRouter()
router.register('candidats', CandidatViewSet)
router.register('formations', FormationViewSet)
router.register('experiences', ExperienceViewSet)
router.register('competences', CompetenceViewSet)
router.register('langues', LangueViewSet)
router.register('certifications', CertificationViewSet)
router.register('projets', ProjetViewSet)
router.register('centres-interet', CentreInteretViewSet)

urlpatterns = router.urls + [
    path('upload-cv/', UploadCVView.as_view(), name='upload-cv'),
]