from rest_framework import filters, viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.tokens import default_token_generator

from .permissions import AdminOnly, AuthorOnly
from .serializers import (RegistrationSerializer, VerifyUserSerializer,
                          UserSerializer, UserPATCHSerializer,
                          UserMeSerializer)
from django.conf import settings

User = get_user_model()


class RegistrationAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user = get_object_or_404(User, username=request.data.get('username'))
        confirmation_code = default_token_generator.make_token(user)

        subject = 'YaMDB'
        message = 'Ваш очень секретный код - ' + confirmation_code

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email, ],
            fail_silently=False,
        )

        return Response(
            {'username': user.username, 'email': user.email},
            status=status.HTTP_200_OK
        )


class UserActivateAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = VerifyUserSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            username = serializer.data.get('username')
            user = get_object_or_404(User, username=username)
            user.is_active = True
            user.save()
            refresh = RefreshToken.for_user(user)
            token = str(refresh.access_token)
        return Response({
            'token': token
        }, status=status.HTTP_201_CREATED)


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (AdminOnly,)
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)


@api_view(['GET', 'PATCH'])
@permission_classes([AuthorOnly | AdminOnly])
def user_me(request):
    if request.method == 'PATCH':
        serializer = UserMeSerializer(request.user, data=request.data,
                                      partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
    me = get_object_or_404(User, username=request.user)
    serializer = UserSerializer(me, many=False)
    return Response(serializer.data)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([AdminOnly])
def user_username(request, username):
    user = get_object_or_404(User, username=username)
    if request.method == 'GET':
        serializer = UserPATCHSerializer(user, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    if request.method == 'PATCH':
        serializer = UserSerializer(user, data=request.data,
                                    partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
    user.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
