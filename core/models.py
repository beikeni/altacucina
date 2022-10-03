from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.functions import Lower
from django.utils.translation import gettext as _
from rest_framework.authtoken.models import Token


class Platform(models.TextChoices):
    NETFLIX = 'netflix', _('Netflix')
    PRIME_VIDEO = 'prime_video', _('Prime Video')
    HBO = 'hbo', _('HBO')
    CBS = 'cbs', _('CBS')
    HULU = 'hulu', _('HULU')


class TimestampMixin:
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class Movie(TimestampMixin, models.Model):
    users = models.ManyToManyField(get_user_model(), through="core.Watched", related_name="movies")
    name = models.CharField(max_length=100)
    year = models.IntegerField()
    platform = models.CharField(max_length=20, choices=Platform.choices)

    class Meta:
        constraints = [
            models.UniqueConstraint(Lower('name'), 'year', name='unique_movie')
        ]

    def __str__(self):
        return f"{self.name.title()}({self.year})"


class Watched(TimestampMixin, models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="watched")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="watched")


class Review(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="reviews")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="reviews")
    body = models.CharField(max_length=280)
    score = models.IntegerField(validators=[MaxValueValidator(10), MinValueValidator(1)])

    class Meta:
        constraints = [
            models.UniqueConstraint('user', 'movie', name='unique_user_movie_review')
        ]

    def __str__(self):
        return f"{self.movie} - {self.score}"
