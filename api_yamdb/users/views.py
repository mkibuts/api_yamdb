import random

from django.core.mail import send_mail
from rest_framework import viewsets, status, permissions
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (RegistrationSerializer, VerifyUserSerializer,
                          UserSerializer)
from .models import User


class RegistrationAPIView(APIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegistrationSerializer

    def generate_code(self):
        random.seed()
        return str(random.randint(100000, 999999))

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        email = serializer.initial_data.get('email')
        username = serializer.initial_data.get('username')
        if User.objects.filter(username=username, email=email).exists():
            user = get_object_or_404(User, username=username)
            confirmation_code = self.generate_code()
            user.confirmation_code = confirmation_code
            user.save()
            email = user.email
        else:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            confirmation_code = get_object_or_404(
                User,
                username=serializer.data.get('username')
            ).confirmation_code
            email = serializer.data.get('email')

        subject = 'YaMDB'
        message = 'Ваш очень секретный код - ' + confirmation_code

        send_mail(
            subject,
            message,
            'from@yamdb.ru',
            [email, ],
            fail_silently=False,
        )

        return Response(
            {'username': username, 'email': email},
            status=status.HTTP_201_CREATED
        )


class UserActivateAPIView(APIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = VerifyUserSerializer

    def post(self, request):
        serializer = VerifyUserSerializer(data=request.data)
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
    permission_classes = (permissions.IsAdminUser,)
    queryset = User.objects.all()
    serializer_class = UserSerializer


@api_view(['GET', 'PATCH'])
def user_me(request):
    if request.method == 'PATCH':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
    me = get_object_or_404(User, username=request.data.get('username'))
    serializer = UserSerializer(me, many=False)
    return Response(serializer.data)


@api_view(['GET', 'PATCH', 'DELETE'])
def user_username(request, username):
    user = get_object_or_404(User, username=username)
    if request.method == 'GET':
        serializer = UserSerializer(user, many=False)
        return Response(serializer.data)
    serializer = UserSerializer(data=request.data)
    if request.method == 'PATCH':
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
    user.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
