from core.viewsets import MovieViewSet, ReviewViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register('movies', MovieViewSet)
router.register('reviews', ReviewViewSet)