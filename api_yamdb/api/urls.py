from rest_framework import routers
from django.urls import path, include

from .views import (ReviewViewSet, CommentViewSet)

router = routers.DefaultRouter()
router.register(r'v1/titles/(?P<title_id>\d+)/reviews', ReviewViewSet)
router.register(
    r'v1/titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet
)

urlpatterns = [
    path('', include(router.urls)),
]
