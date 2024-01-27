from django.conf import settings

def get_google_api(request):
    return {'GOOGLE_API_KEY': settings.GOOGLE_API_KEY} #zwroci key w zrodle strony w script (templates/vendor/base/)