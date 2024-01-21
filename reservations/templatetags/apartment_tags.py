from django import template
from reservations.models import Apartment

register = template.Library()

@register.filter
def if_user_offer_apartment(user):
    if user.is_authenticated:
        return Apartment.objects.filter(user=user).exists()
    return False