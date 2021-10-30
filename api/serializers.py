from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import Category, Comment, Genre, Review, Title, User


class SelfUserSerializer(ModelSerializer):
    role = serializers.CharField(read_only=True)
    username = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name',
            'bio', 'email',
            'username', 'role'
        )


class UserSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'username',
            'bio', 'email', 'role'
        )


class AuthUserSerializer(ModelSerializer):
    confirmation_code = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'username', 'email',
            'role', 'confirmation_code'
        )


class UpdateConfirmationCodeSerializer(ModelSerializer):
    confirmation_code = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('confirmation_code', )


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = ('id',)


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        exclude = ('id',)


class TitleReadSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField()

    class Meta:
        fields = ('id',
                  'name',
                  'year',
                  'rating',
                  'description',
                  'genre',
                  'category')
        model = Title


class TitleWriteSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
        required=False,
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
        required=False
    )

    class Meta:
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        many=False,
        required=False,
        default=serializers.CurrentUserDefault()
    )

    def validate(self, data):
        if self.context['request'].method == 'POST':
            title = get_object_or_404(
                Title,
                id=self.context['request'].parser_context['kwargs']['title_id']
            )
            review = Review.objects.filter(
                author=self.context['request'].user,
                title=title
            ).exists()
            if review:
                raise serializers.ValidationError(
                    'Пользователь может оставить'
                    'только один отзыв на один объект.'
                )
        return data

    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ['title']


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        many=False
    )

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ['review', ]
