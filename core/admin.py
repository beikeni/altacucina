from django.contrib import admin

# Register your models here.
from django.contrib.auth import get_user_model

from core.models import Movie, Review


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    model = Movie


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    model = Review
