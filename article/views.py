from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator

from .forms import ArticleForm
from .models import Article, ArticleColumn
from comment.forms import CommentForm
from taggit.models import Tag  # 标签模型


# 获取侧边栏内容
def get_side_content(request):
    '''
    获取侧边栏内容
    :param request:
    :return: 侧边栏内容
    '''
    # 获取按年月归档博客及其数量
    article_dates = Article.objects.dates('created', 'month', order='DESC')
    article_dates_dict = {}
    for article_date in article_dates:
        article_count = Article.objects.filter(created__year=article_date.year,
                                               created__month=article_date.month).count()
        article_dates_dict[article_date] = article_count

    context = {}

    context['article_dates'] = article_dates_dict

    # 获取博客种类和每种博客的数量
    # context['blog_types'] = BlogType.objects.annotate(blog_count=Count('blog'))

    # 获取阅读量最高的文章
    context['hot_articles'] = Article.objects.all().order_by('-total_views')[:5]

    # 获取所有标签
    tags = Tag.objects.all()
    context['tags'] = tags

    return context


def get_articles_common(request, articles_all_list):
    '''
    分页
    :param request:
    :param articles_all_list: 文章列表
    :return: 返回对应页的文章列表
    '''
    paginator = Paginator(articles_all_list, 11)  # 分页
    page_num = request.GET.get('page', 1)
    current_page = paginator.get_page(page_num)  # 获取当前页
    current_page_num = current_page.number  # 获取当前页码
    # 当前页和前后各两页的页码
    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + list(
        range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))

    # 添加省略标记
    if page_range[0] - 1 >= 2:
        page_range.insert(0, '···')
    if paginator.num_pages - page_range[-1] > 1:
        page_range.append('···')

    # 加上首页和尾页
    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    # print(type(articles.paginator))  # django.core.paginator.Paginator

    # 获取侧边栏内容
    context = get_side_content(request)

    context['articles'] = current_page.object_list  # 当前页中的所有文章
    context['page_range'] = page_range
    context['current_page'] = current_page

    return context


def article_list(request):
    '''
    获取文章列表
    :param request:
    :return: 文章列表
    '''
    search = request.GET.get("search")

    # 初始化查询集
    articles_list = Article.objects.all().order_by('-created')
    if search:
        articles_list = Article.objects.filter(
            Q(title__icontains=search) | Q(body__icontains=search)).order_by('-total_views')
    else:
        search = ''

    context = get_articles_common(request, articles_list)
    context['search'] = search

    return render(request, 'article/article_list.html', context)


def article_with_date(request, year, month):
    '''
    获取某个归档下的所有文章
    :param request:
    :param year: 年
    :param month: 月
    :return: 某个归档下的所有文章
    '''
    articles_list = Article.objects.filter(created__year=year, created__month=month).order_by('-created')
    context = get_articles_common(request, articles_list)
    return render(request, 'article/article_list.html', context)


def article_with_tags(request, id):
    '''
    获取某个标签的所有文章
    :param request:
    :param id: 标签的id
    :return: 某个标签的所有文章
    '''
    tag = get_object_or_404(Tag, id=id)
    articles_list = Article.objects.filter(tags__name__in=[tag.name])
    context = get_articles_common(request, articles_list)
    return render(request, 'article/article_list.html', context)


def article_with_column(request, id):
    '''
    获取某个栏目的所有文章
    :param request:
    :param id: 栏目id
    :return: 某个栏目的所有文章
    '''
    column = get_object_or_404(ArticleColumn, id=id)
    articles_list = Article.objects.filter(column=column)
    context = get_articles_common(request, articles_list)
    context['column'] = column
    return render(request, 'article/article_list.html', context)


def article_detail(request, id):
    '''
    文章详情页面的视图函数
    :param request:
    :param id: 文章的id
    :return: 详情页内容
    '''
    article = get_object_or_404(Article, id=id)
    article.total_views += 1
    article.save()

    # 前一篇和后一篇文章
    previous_article = Article.objects.filter(created__gt=article.created).last()
    next_article = Article.objects.filter(created__lt=article.created).first()
    comments = article.comments.all()  # 获取该文章的所有评论
    comment_form = CommentForm()

    context = {
        'previous': previous_article,
        'next': next_article,
        'article': article,
        'comments': comments,
        'comment_form': comment_form,
    }

    context.update(get_side_content(request))

    return render(request, 'article/article_detail.html', context)


def give_likes(request, id):
    '''
    点赞
    :param request:
    :param id: 文章id
    :return:
    '''
    article = get_object_or_404(Article, id=id)
    article.likes += 1
    article.save()
    return HttpResponse('success')


# 写文章
@login_required(login_url='/accounts/login')
def article_create(request):
    '''
    获取写文章页面
    :param request:
    :return: 写文章页面
    '''
    if not request.user.is_superuser:
        return HttpResponse("<h2>{}</h2>".format('对不起，您没有该权限'))
    if request.method == "POST":
        article_form = ArticleForm(data=request.POST, files=request.FILES)
        if article_form.is_valid():
            cd = article_form.cleaned_data
            new_article = article_form.save(commit=False)
            new_article.author = request.user

            new_article.save()
            # 保存 tags 的多对多关系
            article_form.save_m2m()

            return redirect(new_article)
        else:
            return HttpResponse('3')
    else:
        columns = ArticleColumn.objects.all()
        article_form = ArticleForm()
        context = {
            'columns': columns,
            'article_form': article_form,
        }
        return render(request, 'article/article_create.html', context)


# 更新文章
@login_required(login_url='/accounts/login')
def article_update(request, id):
    """
    更新文章的视图函数
    id： 文章的 id
    """
    if not request.user.is_superuser:
        return HttpResponse("<h2>{}</h2>".format('对不起，您没有该权限'))

    # 获取需要修改的具体文章对象
    article = get_object_or_404(Article, id=id)
    # 判断用户是否为 POST 提交表单数据
    if request.method == "POST":
        # 将提交的数据赋值到表单实例中
        article_form = ArticleForm(data=request.POST, files=request.FILES)
        # 判断提交的数据是否满足模型的要求
        if article_form.is_valid():
            cd = article_form.cleaned_data
            # 保存新写入的 title、body 数据并保存
            article.title = cd.get('title')
            article.body = cd.get('body')

            # 修改栏目
            article.column = ArticleColumn.objects.get(id=request.POST['column'])

            # 修改标签
            article.tags.clear()
            for tag in request.POST['tags'].split(','):
                article.tags.add(tag)

            if cd.get('cover'):
                article.cover = cd.get('cover')

            article.save()
            # 完成后返回到修改后的文章中。需传入文章的 id 值
            return redirect("article:detail", id=id)
        # 如果数据不合法，返回错误信息
        else:
            return HttpResponse("表单内容有误，请重新填写。")

    # 如果用户 GET 请求获取数据
    else:
        # 创建表单类实例
        article_form = ArticleForm()
        columns = ArticleColumn.objects.all()
        # 赋值上下文，将 article 文章对象也传递进去，以便提取旧的内容
        context = {'article': article, 'article_form': article_form, 'columns': columns}
        # 将响应返回到模板中
        return render(request, 'article/article_update.html', context)


# 添加栏目的接口
@login_required(login_url='/accounts/login/')
def add_column(request):
    '''
    添加栏目的接口
    :param request:
    :return: 新栏目的id和名称
    '''
    if not request.user.is_superuser:
        return HttpResponse("<h2>{}</h2>".format('对不起，您没有该权限'))
    new_column = ArticleColumn.objects.create(title=request.POST['new_column'])
    new_column.save()
    return JsonResponse({"column_id": new_column.id, "column_name": new_column.title})


def categories(request):
    '''
    文章分类页面视图函数
    :param request:
    :return: 文章分类页面
    '''
    columns = ArticleColumn.objects.all()
    context = get_side_content(request)
    context['columns'] = columns
    return render(request, 'article/categories.html', context)


