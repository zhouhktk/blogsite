from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from notifications.signals import notify

from article.models import Article
from .models import Comment
from .forms import CommentForm


@login_required(login_url='/accounts/login/')
def post_comment(request, article_id, parent_comment_id=None):
    article = get_object_or_404(Article, id=article_id)
    # 处理post请求
    if request.method == "POST":
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.article = article
            new_comment.user = request.user

            # 二级回复
            if parent_comment_id:
                parent_comment = get_object_or_404(Comment, id=parent_comment_id)
                # 若回复超过两级则置为两级
                new_comment.parent = parent_comment.get_root()
                # 被回复人
                new_comment.reply_to = parent_comment.user
                new_comment.save()

                # 新增代码，给其他用户发送通知
                if not parent_comment.user.is_superuser:
                    # 判断父级是否和被回复者是否相同
                    if parent_comment.user.id == new_comment.reply_to.id:
                        recipient = parent_comment.user
                    else:
                        recipient = [parent_comment.user, new_comment.reply_to]
                    notify.send(
                        request.user,
                        recipient=recipient,
                        verb='回复了你',
                        target=article,
                        action_object=new_comment,
                    )
                    # print("发送给用户")

                return JsonResponse({"code": "200 OK", "new_comment_id": new_comment.id})
            new_comment.save()
            # 新增代码，给管理员发送通知
            if not request.user.is_superuser:
                notify.send(
                    request.user,
                    recipient=User.objects.filter(is_superuser=1),
                    verb='回复了你',
                    target=article,
                    action_object=new_comment,
                )
                # print("发送管理员")
            redirect_url = article.get_absolute_url() + '#comment_elem_' + str(new_comment.id)

            return redirect(redirect_url)
        else:
            return HttpResponse("表单内容有误，请重新填写。")
    elif request.method == 'GET':
        comment_form = CommentForm()
        context = {'comment_form': comment_form, 'article_id': article_id, 'parent_comment_id': parent_comment_id}
        return render(request, 'comment/reply.html', context)
