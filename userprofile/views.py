from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

from .models import UserProfile


@login_required(login_url='/accounts/login/')
def profile_update(request):
    if UserProfile.objects.filter(user=request.user).exists():
        userprofile = get_object_or_404(UserProfile, user=request.user)
    else:
        userprofile = UserProfile.objects.create(user=request.user)

    if request.method == "POST":
        userprofile.avatar = request.FILES.get('avatar')
        # print(userprofile.avatar.url)
        userprofile.save()
        # return redirect('userprofile:profile')
        return JsonResponse({"avatarurl": userprofile.avatar.url})
    elif request.method == 'GET':
        return render(request, 'account/profile.html')


