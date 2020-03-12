from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from taggit.managers import TaggableManager

from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit


class ArticleColumn(models.Model):
    """
    栏目的 Model
    """
    # 栏目标题
    title = models.CharField(max_length=100, blank=True)
    # 创建时间
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title


# 博客文章数据模型
class Article(models.Model):
    # 文章作者。参数 on_delete 用于指定数据删除的方式
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    # 文章标题
    title = models.CharField(max_length=300)

    # 文章正文
    body = models.TextField()

    # 文章创建时间。参数 default=timezone.now 指定其在创建数据时将默认写入当前的时间
    created = models.DateTimeField(default=timezone.now)

    # 文章更新时间。参数 auto_now=True 指定每次数据更新时自动写入当前时间
    updated = models.DateTimeField(auto_now=True)

    # 阅读量
    total_views = models.PositiveIntegerField(default=0)

    # 点赞数
    likes = models.PositiveIntegerField(default=0)

    # 文章栏目的 “一对多” 外键
    column = models.ForeignKey(ArticleColumn, null=True, blank=True, on_delete=models.CASCADE, related_name='article')

    # 标签
    tags = TaggableManager(blank=True)

    # 封面图
    cover = ProcessedImageField(
        upload_to='article/cover/%Y%m%d',
        processors=[ResizeToFit(width=400)],
        format='JPEG',
        options={'quality': 80},
        blank=True
    )

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.title

    # 返回文章的绝对路径
    def get_absolute_url(self):
        return reverse('article:detail', args=(self.id,))
