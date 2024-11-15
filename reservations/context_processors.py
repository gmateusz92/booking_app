from django.conf import settings
from accounts.models import UserProfile


def get_google_api(request):
    return {'GOOGLE_API_KEY': settings.GOOGLE_API_KEY} #zwroci key w zrodle strony w script (templates/vendor/base/)


# def profile(request):
#     if request.user.is_authenticated:
#         profile = UserProfile.objects.get(user=request.user)  # Przykładowe pobranie profilu
#     else:
#         profile = None
#     return {'profile': profile}



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
