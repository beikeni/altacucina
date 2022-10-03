from django.contrib.auth import get_user_model
from django.db.models import Avg
from rest_framework import serializers
from .models import Movie, Watched, Review


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ('id', 'name', 'year', 'platform')


class MovieWithAverageScoreSerializer(serializers.ModelSerializer):
    average_score = serializers.SerializerMethodField()

    def get_average_score(self, movie):
        return movie.reviews.aggregate(Avg('score'))['score__avg']

    class Meta:
        model = Movie
        fields = ('id', 'name', 'year', 'platform', 'average_score')


class WatchedMovieSerializer(serializers.ModelSerializer):
    is_watched = serializers.SerializerMethodField()

    def get_is_watched(self, movie):
        return movie.watched.filter(user_id=self.context['request'].user).exists()

    class Meta:
        model = Movie
        fields = ['id', 'name', 'year', 'platform', 'is_watched']


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['body', 'score', 'movie']
        read_only_fields = ['user', ]
