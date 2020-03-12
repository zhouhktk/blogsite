# -*- coding:utf-8 -*-
from django.urls import path
from . import views

app_name = 'userprofile'
urlpatterns = [
    path('profile/', views.profile_update, name='profile'),
]
