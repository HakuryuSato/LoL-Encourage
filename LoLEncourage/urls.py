from django.contrib import admin
from django.urls import path, include
from .views import view_home

app_name = 'LoLEncourage'

urlpatterns = [
    path('', view_home, name='home'),
]