from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .models import ContentImage


@csrf_exempt
@login_required(login_url='/accounts/login/')
def upload(request):
    if not request.user.is_superuser:
        return HttpResponse("<h2>{}</h2>".format('对不起，您没有该权限'))
    image = request.FILES.get('editormd-image-file', None)
    # print(request.FILES)
    # print(image.name)
    image = ContentImage.objects.create(image=image)
    image.save()
    print(image.image.url)
    res = {'success': 1, 'message': '图片上传成功', 'url': image.image.url}
    return JsonResponse(res)
