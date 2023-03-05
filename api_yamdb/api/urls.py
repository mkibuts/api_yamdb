from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CategoryViewSet, GenreViewSet, TitleViewSet,
                    ReviewViewSet, CommentViewSet, RegistrationAPIView,
                    UserActivateAPIView, UserViewSet, user_me, user_username)
from .permissions import AdminOnly

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'genres', GenreViewSet, basename='genres')
router.register(r'titles', TitleViewSet, basename='titles')
router.register(r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet
)
router.register('users', UserViewSet)

app_name = 'api'

urlpatterns = [
    path('v1/users/me/', user_me),
    path('v1/users/<username>/', user_username),
    path('v1/', include(router.urls)),
    path('v1/auth/signup/', RegistrationAPIView.as_view()),
    path('v1/auth/token/', UserActivateAPIView.as_view()),

]
