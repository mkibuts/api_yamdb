import random

from django.core.mail import send_mail
from rest_framework import viewsets, status, permissions, filters
from rest_framework.generics import get_object_or_404
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .permissions import AdminOnly
from .serializers import (RegistrationSerializer, VerifyUserSerializer,
                          UserSerializer, UserMeSerializer)


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
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AdminOnly,)
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('$name',)

    def update(self, request, *args, **kwargs):
        if self.request.method == 'PUT':
            raise MethodNotAllowed('PUT')
        return super().update(request, *args, **kwargs)


class UserMeAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = self.request.user
        serializer = UserMeSerializer(user)
        return Response(serializer.data)

    def patch(self, request):
        user = self.request.user
        serializer = UserMeSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



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
