from django.contrib import admin
from .models import Article, ArticleColumn


admin.site.register(ArticleColumn)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created', 'updated')
