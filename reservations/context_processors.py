from django.conf import settings
from accounts.models import UserProfile


def get_google_api(request):
    return {'GOOGLE_API_KEY': settings.GOOGLE_API_KEY} #zwroci key w zrodle strony w script (templates/vendor/base/)


def profile(request):
    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user=request.user)  # Przykładowe pobranie profilu
    else:
        profile = None
    return {'profile': profile}