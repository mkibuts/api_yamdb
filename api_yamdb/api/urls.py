from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (CategoryViewSet, GenreViewSet, TitleViewSet,
                    ReviewViewSet, CommentViewSet)
from users.views import (RegistrationAPIView, UserActivateAPIView, UserViewSet,
                         user_me, user_username)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'genres', GenreViewSet)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet
)
router.register('users', UserViewSet)
router.register(r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet)
router.register(r'titles', TitleViewSet, basename='titles')
urlpatterns = [
    path('v1/users/me/', user_me),
    path('v1/users/<username>/', user_username),
    path('v1/auth/signup/', RegistrationAPIView.as_view()),
    path('v1/auth/token/', UserActivateAPIView.as_view()),
    path('v1/', include(router.urls)),
]
