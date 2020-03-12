# -*- coding:utf-8 -*-
from django.urls import path
from . import views

app_name = 'article'
urlpatterns = [
    path('list/', views.article_list, name='list'),
    path('list/<int:year>/<int:month>/', views.article_with_date, name='article_with_date'),
    path('detail/<int:id>/', views.article_detail, name='detail'),
    path('tags/<int:id>/', views.article_with_tags, name='article_with_tags'),
    path('columns/<int:id>/', views.article_with_column, name='article_with_column'),
    path('create/', views.article_create, name='create'),
    path('update/<int:id>/', views.article_update, name='update'),
    path('add_column/', views.add_column, name='add_column'),
    path('categories/', views.categories, name='categories'),
    path('give-likes/<int:id>/', views.give_likes, name='give_likes'),
]
