from django.urls import include, path
from rest_framework import routers

from .views import (AuthTokenView, AuthUserView, CategoryViewSet,
                    CommentViewSet, GenreViewSet, ReviewViewSet, TitleViewSet,
                    UserViewSet)

router_v1 = routers.DefaultRouter()
router_v1.register('users', UserViewSet, basename='users')
router_v1.register('titles', TitleViewSet, basename='title')
router_v1.register('categories', CategoryViewSet, basename='category')
router_v1.register('genres', GenreViewSet, basename='genre')
router_v1.register('reviews', ReviewViewSet, basename='review')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='title_reviews'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='review_comments'
)
router_v1.register('comments', CommentViewSet, basename='comment')

authorization = [
    path('auth/email/', AuthUserView.as_view(), name='get_confirmation_code'),
    path('auth/token/', AuthTokenView.as_view(), name='get_jwt_token')
]

urlpatterns = [
    path('v1/', include(authorization)),
    path('v1/', include(router_v1.urls)),
]
