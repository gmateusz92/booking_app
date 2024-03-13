from vendor.models import Vendor, UserProfile
from django.conf import settings


#context processors zawsze rejestruje sie w settings

def get_vendor(request):
    try:                     #zeby nie bylo bledu gdy uzytkownik bedzie wylogowany
        vendor = Vendor.objects.get(user=request.user)
    except:
        vendor = None
    return dict(vendor=vendor)

def get_user_profile(request):
    try:                     #zeby nie bylo bledu gdy uzytkownik bedzie wylogowany
        user_profile = UserProfile.objects.get(user=request.user)
    except:
        user_profile = None
    return dict(user_profile=user_profile)

# pobiera klucz API google
def get_google_api(request):
    return {'GOOGLE_API_KEY': settings.GOOGLE_API_KEY} #zwroci key w zrodle strony w script (templates/vendor/base/)

#pobiera klucz API Paypal
def get_paypal_client_id(request):
    return {'PAYPAL_CLIENT_ID': settings.PAYPAL_CLIENT_ID}

from .models import UserProfile

# def profile(request):
#     if request.user.is_authenticated:
#         profile = UserProfile.objects.get(user=request.user)  # Przykładowe pobranie profilu
#     else:
#         profile = None
#     return {'profile': profile}

def profile(request):
    profile = None
    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=request.user)
            if not profile.profile_picture:  # Sprawdzamy, czy użytkownik ma przypisane zdjęcie profilowe
                profile = None  # Jeśli nie, ustawiamy profile na None
        except UserProfile.DoesNotExist:
            pass
    return {'profile': profile}