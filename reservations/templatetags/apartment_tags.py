from datetime import date

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


@register.filter(name="if_owner_has_bookings")
def if_owner_has_bookings(user, apartment):
    # Sprawdź, czy użytkownik jest właścicielem apartamentu
    if apartment.user == user:
        # Sprawdź, czy istnieje rezerwacja dla tego apartamentu
        if Booking.objects.filter(name=apartment).exists():
            return True
    return False


@register.filter
def if_user_has_booking_history(user):
    return Booking.objects.filter(user=user, check_out__lt=date.today()).exists()
