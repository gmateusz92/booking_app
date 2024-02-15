from django import template
from reservations.models import Apartment, Booking

register = template.Library()

@register.filter
def if_user_offer_apartment(user):
    if user.is_authenticated:
        return Apartment.objects.filter(user=user).exists()
    return False


@register.filter
def if_user_has_bookings(user):
    return Booking.objects.filter(user=user).exists()