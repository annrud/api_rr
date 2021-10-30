import random
import string

from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (SAFE_METHODS, IsAdminUser,
                                        IsAuthenticated)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from api_yamdb import settings

from .filters import TitleFilter
from .models import Category, Comment, Genre, Review, Title, User
from .permissions import IsAuthorOrIsAuthenticatedOrReadOnly, ReadOnly
from .serializers import (AuthUserSerializer, CategorySerializer,
                          CommentSerializer, GenreSerializer, ReviewSerializer,
                          SelfUserSerializer, TitleReadSerializer,
                          TitleWriteSerializer,
                          UpdateConfirmationCodeSerializer, UserSerializer)


class AuthUserView(APIView):
    @staticmethod
    def post(request):
        email = request.data.get('email')
        confirmation_code = ''.join(
            random.choices(string.digits + string.ascii_uppercase, k=6)
        )
        try:
            user = User.objects.get(email=email)
            data = {'confirmation_code': confirmation_code}
            serializer = UpdateConfirmationCodeSerializer(
                instance=user, data=data
            )
            subject = 'Yamdb. Код подтверждения'
            message = f'Код подтверждения: {confirmation_code}'
        except User.DoesNotExist:
            data = {'email': email, 'confirmation_code': confirmation_code,
                    'username': email}
            serializer = AuthUserSerializer(data=data)
            subject = 'Регистрация на YaMDB'
            message = (
                'Спасибо за регистрацию в Yamdb.'
                f'Код подтверждения: {confirmation_code}'
            )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=True,
        )
        return Response({'email': email})


class AuthTokenView(APIView):
    @staticmethod
    def post(request):
        user = get_object_or_404(
            User, email=request.data.get('email'),
            confirmation_code=request.data.get('confirmation_code')
        )
        response = {'token': str(AccessToken().for_user(user))}
        return Response(response, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = 'username'
    lookup_value_regex = '[^/]+'
    permission_classes = (IsAdminUser,)

    @action(detail=False, permission_classes=(IsAuthenticated,),
            methods=['get', 'patch'], url_path='me')
    def get_or_update_self(self, request):
        if request.method != 'GET':
            serializer = SelfUserSerializer(
                instance=request.user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        else:
            serializer = SelfUserSerializer(request.user)
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthorOrIsAuthenticatedOrReadOnly]
    pagination_class = PageNumberPagination

    def get_queryset(self, *args, **kwargs):
        title = get_object_or_404(Title, id=self.kwargs['title_id'])
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs['title_id'])
        serializer.save(author=self.request.user, title=title)

    def perform_update(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs['title_id'])
        serializer.save(title=title)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrIsAuthenticatedOrReadOnly]
    pagination_class = PageNumberPagination

    def get_queryset(self, *args, **kwargs):
        review = get_object_or_404(Review, id=self.kwargs['review_id'])
        return super().get_queryset().filter(review=review)

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs['review_id'])
        serializer.save(author=self.request.user, review=review)

    def perform_update(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs['review_id'])
        serializer.save(review=review)


class TaxonViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    filter_backends = [SearchFilter]
    search_fields = ('=name',)
    lookup_field = 'slug'
    permission_classes = (IsAdminUser | ReadOnly,)


class CategoryViewSet(TaxonViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(TaxonViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).order_by('id')
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = (IsAdminUser | ReadOnly,)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return TitleReadSerializer
        return TitleWriteSerializer
