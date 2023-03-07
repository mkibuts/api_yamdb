from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
import random
from rest_framework.decorators import api_view, permission_classes

from .filters import TitlesFilter
from .mixins import ListCreateDestroyViewSet
from reviews.models import Category, Genre, Title, Review, Comment
from .permissions import (
    IsAdminOrReadOnly,
    AdminOnly,
    ModeratorOnly,
    AuthorOnly,
    AnonymousReadOnly,
    AuthenticationReadOnly
)
from .serializers import (
    CategorySerializer,
    TitleSerializer,
    GenreSerializer,
    ReviewSerializer,
    CommentSerializer,
    RegistrationSerializer,
    VerifyUserSerializer,
    UserSerializer,
    # UserPATCHSerializer
)

User = get_user_model()


class CategoryViewSet(ListCreateDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"


class GenreViewSet(ListCreateDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(
        Avg("reviews__score")
    ).order_by("name")
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitlesFilter


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return Review.objects.filter(title=title)


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
    search_fields = ('username', )


@api_view(['GET', 'PATCH'])
@permission_classes([AuthenticationReadOnly | AuthorOnly | AdminOnly])
def user_me(request):
    if request.method == 'PATCH':
        serializer = UserSerializer(data=request.data, partial=True)
        # if not serializer.initial_data.get('username'):
        #     username = request.user.username
        # if not serializer.initial_data.get('email'):
        #     email = request.user.email
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
        serializer = UserSerializer(user, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    serializer = UserSerializer(data=request.data)
    if request.method == 'PATCH':
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
    user.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# class UserMeAPIView(APIView):
#     # permission_classes = (AuthenticationReadOnly, AuthorOnly, AdminOnly)
#     permission_classes = (AuthorOnly, )
#     serializer_class = UserSerializer
#
#     def get(self, request):
#         me = get_object_or_404(User, username=request.user)
#         serializer = UserSerializer(me, many=False)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#     def patch(self, request):
#         serializer = UserSerializer(data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
