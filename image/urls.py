# -*- coding:utf-8 -*-
from django.urls import path
from . import views

app_name = 'image'
urlpatterns = [
    path('upload/', views.upload, name='upload'),
]
