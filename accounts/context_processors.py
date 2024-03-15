from django.conf import settings
from .models import UserProfile


def get_user_profile(request):
    try:                     
        user_profile = UserProfile.objects.get(user=request.user)
    except:
        user_profile = None
    return dict(user_profile=user_profile)


def get_google_api(request):
    return {'GOOGLE_API_KEY': settings.GOOGLE_API_KEY} #zwroci key w zrodle strony w script (templates/vendor/base/)



# def profile(request):
#     profile = None
#     if request.user.is_authenticated:
#         try:
#             profile = UserProfile.objects.get(user=request.user)
#             if not profile.profile_picture: 
#                 profile = None  
#         except UserProfile.DoesNotExist:
#             pass
#     return {'profile': profile}

from django.contrib.auth.models import User
from .models import UserProfile

def profile(request):
    user = request.user
    if user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=user)
        return {'profile': profile}
    else:
        return {}