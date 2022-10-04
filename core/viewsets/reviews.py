import functools

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from core.models import Review, Movie
from core.serializers import ReviewSerializer, ReviewWatchedMovieSerializer


class ReviewViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, GenericViewSet):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()
    permission_classes = [IsAuthenticated, ]

    def filter_queryset(self, queryset):
        ordering = self.request.GET.get("ordering", None)

        # ['id', '-id', 'user', '-user' ...
        order_options = [prefix + field.name for field in Review._meta.fields for prefix in ['', '-']]

        if ordering in order_options:
            queryset = queryset.order_by(ordering)
        return queryset

    def get_custom_queryset(self, instance):
        return instance.reviews.all()

    @action(methods=['get'], detail=False, url_path='movie/(?P<id>[^/.]+)', url_name="list-movie-reviews",
            permission_classes=[IsAuthenticatedOrReadOnly])
    def list_movie_reviews(self, request, *args, **kwargs):
        """Returns all reviews for a given movie"""

        movie = get_object_or_404(Movie, id=kwargs['id'])
        serializer = ReviewWatchedMovieSerializer(self.filter_queryset(self.get_custom_queryset(movie)), many=True,
                                                  context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False, url_path='user/(?P<id>[^/.]+)', url_name="list-user-reviews",
            permission_classes=[IsAuthenticatedOrReadOnly])
    def list_user_reviews(self, request, *args, **kwargs):
        """Returns all reviews for a given user"""

        user = get_object_or_404(get_user_model(), id=kwargs['id'])
        serializer = self.serializer_class(self.filter_queryset(self.get_custom_queryset(user)), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        """Override for inferring the user from the request"""

        serializer.save(user_id=self.request.user.id)

    def create(self, request, *args, **kwargs):
        """Override for enforcing one review for user/movie pair"""

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except IntegrityError as e:
            if 'unique_user_movie_review' in e.args[0]:
                return Response({'error': 'Max 1 review per user/movie pair'}, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({'error': 'Unknown error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
