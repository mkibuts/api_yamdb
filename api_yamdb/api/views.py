from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings

from reviews.models import Category, Genre, Title, Review, Comment
from .permissions import AdminOrReadOnly, AdminOnly, IsAuthorOrStaffOrReadOnly
from .filters import TitleFilter
from .mixins import ListCreateDestroyViewSet
from .serializers import (ReviewSerializer, CommentSerializer,
                          TitleReadSerializer, TitleCreateSerializer,
                          GenreSerializer, CategorySerializer,
                          RegistrationSerializer, VerifyUserSerializer,
                          UserSerializer, UserPATCHSerializer,
                          UserMeSerializer
                          )


User = get_user_model()


class CategoryViewSet(ListCreateDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          AdminOrReadOnly,)
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('$name',)


class GenreViewSet(ListCreateDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          AdminOrReadOnly,)
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('$name',)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(
        Avg('reviews__score')
    ).order_by('name')
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          AdminOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PUT', 'PATCH'):
            return TitleCreateSerializer
        return TitleReadSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews.all()


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        return Comment.objects.filter(review=review)


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
@permission_classes([IsAuthorOrStaffOrReadOnly])
def user_me(request):
    if request.method == 'PATCH':
        serializer = UserMeSerializer(request.user, data=request.data,
                                      partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
    if not request.user.is_authenticated:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
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
