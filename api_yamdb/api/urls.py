from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import RegistrationAPIView, UserActivateAPIView, UserViewSet

router = SimpleRouter()


app_name = 'api'
router.register('users', UserViewSet)

urlpatterns = [
    path('signup/', RegistrationAPIView.as_view()),
    path('token/', UserActivateAPIView.as_view()),
    path('', include(router.urls)),
]
