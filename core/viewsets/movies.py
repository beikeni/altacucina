from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from core.models import Movie
from core.serializers import MovieSerializer, WatchedMovieSerializer, MovieWithAverageScoreSerializer

from django.db import connection, reset_queries
import time
import functools


def query_debugger(func):
    @functools.wraps(func)
    def inner_func(*args, **kwargs):
        reset_queries()

        start_queries = len(connection.queries)

        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()

        end_queries = len(connection.queries)

        print(f"Function : {func.__name__}")
        print(f"Number of Queries : {end_queries - start_queries}")
        print(f"Finished in : {(end - start):.2f}s")
        return result

    return inner_func


class MovieViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, GenericViewSet):
    serializer_class = MovieSerializer
    queryset = Movie.objects.all()

    def get_platform_queryset(self, platform):
        return Movie.objects.filter(platform=platform)

    def get_custom_queryset(self, instance):
        return instance.movies.all()

    @action(methods=['get'], detail=False, url_path='watched', url_name="watched", permission_classes=[IsAuthenticated])
    def list_watched_movies(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.get_custom_queryset(request.user), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False, url_path='platform/(?P<platform>[^/.]+)', url_name="provider")
    def list_platform(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.get_platform_queryset(platform=kwargs['platform']), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @query_debugger
    @action(methods=['get'], detail=False, url_path='unwatched-with-review', url_name="unwatched-with-review",
            permission_classes=[IsAuthenticated])
    def list_unwatched_with_review(self, request, *args, **kwargs):
        """Returns all movies that have not been watched by the authenticated user that have at least one review"""

        serializer = MovieWithAverageScoreSerializer(
            Movie.objects.filter(reviews__isnull=False).exclude(watched__user=request.user).prefetch_related(
                'reviews__user').prefetch_related('watched__user').distinct(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True, url_path='mark-watched', url_name="mark-watched",
            permission_classes=[IsAuthenticated])
    def watched(self, request, *args, **kwargs):
        """Same endpoint to update watched status for a user/movie pair"""

        movie = get_object_or_404(Movie, id=self.kwargs['pk'])
        watched = False
        if request.user in movie.users.all():
            movie.users.remove(request.user)
        else:
            movie.users.add(request.user)
            watched = True
        return Response({
            'response': f'{movie} has been {"added to" if watched else "removed from"} {str(request.user).title()}\'s list!'},
            status=status.HTTP_200_OK)

    @query_debugger
    def list(self, request, *args, **kwargs):
        """Override to serve two different responses depending on whether the user is authenticated or not"""

        serializer_class = self.serializer_class if not request.user.is_authenticated else WatchedMovieSerializer
        serializer = serializer_class(self.queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def list_watched(self, request):
        serializer = self.serializer_class(self.get_custom_queryset(request.user), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except IntegrityError as e:
            if 'unique_movie' in e.args[0]:
                return Response({'error': 'Movie already exists in DB'}, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({'error': 'Unknown error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    #
