from django.urls import path
from . import views
app_name = 'users'
urlpatterns = [
    path("get-details/", views.UserDetailAPI.as_view()),
    path('register/', views.RegisterUserAPIView.as_view()),
]
