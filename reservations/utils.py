from calendar import HTMLCalendar
from datetime import date, datetime

import requests
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from geopy.distance import geodesic

from booking import settings

from .models import Apartment, Booking, NotificationPreference


def get_weather_data(city):
    api_key = "6H8CDM5GQSPVME8X2Z7RGXKNZ"
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}?unitGroup=metric&key={api_key}&contentType=json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None


class Calendar(HTMLCalendar):
    def __init__(self, year=None, month=None, apartment=None):
        self.year = year
        self.month = month
        self.apartment = apartment
        super(Calendar, self).__init__()

    def formatday(self, day, bookings):
        booking_per_day = bookings.filter(
            check_in__day__lte=day, check_out__day__gte=day
        )

        d = ""
        for booking in booking_per_day:
            d += f'<div class="reservation"></div>'

        if day != 0:
            cell_style = (
                "background-color: red;" if booking_per_day else ""
            )  # Dodaj styl dla całej komórki
            return f"<td class='calendar-cell' style='{cell_style}'><span class='date'>{day}  </span><ul> {d} </ul></td>"
        return '<td class="calendar-cell"></td>'

    def formatweek(self, theweek, events):
        week = ""
        for d, weekday in theweek:
            week += self.formatday(d, events)
        return f"<tr> {week} </tr>"

    def formatmonth(self, withyear=True):
        bookings = Booking.objects.filter(
            name=self.apartment, check_in__year=self.year, check_out__month=self.month
        )

        cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
        cal += f"{self.formatmonthname(self.year, self.month, withyear=withyear)}\n"
        cal += f"{self.formatweekheader()}\n"
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f"{self.formatweek(week, bookings)}\n"
        return cal


def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split("-"))
        return date(year, month, day=1)
    return datetime.today()


def check_location(pk):
    # Pobieramy nowo dodany apartament o podanym identyfikatorze (pk)
    apartment = Apartment.objects.get(pk=pk)

    for notification_preference in NotificationPreference.objects.all():
        # Sprawdzamy czy oba obiekty mają ustawione współrzędne
        if (
            notification_preference.location is not None
            and apartment.location is not None
        ):
            # Tworzymy punkt dla lokalizacji apartamentu i lokalizacji użytkownika
            apartment_point = apartment.location
            user_point = notification_preference.location
            print(apartment_point, user_point)
            # Obliczamy odległość między lokalizacją apartamentu a lokalizacją użytkownika
            distance = geodesic(
                (user_point.y, user_point.x), (apartment_point.y, apartment_point.x)
            ).kilometers
            print(distance)
            # Sprawdzamy czy odległość jest mniejsza lub równa radiusowi z NotificationPreference
            if distance <= notification_preference.radius:
                # Wysyłamy powiadomienie e-mail
                subject = "Nowy apartament w pobliżu"
                message = render_to_string(
                    "emails/notification_email.html",
                    {"apartment": apartment, "distance": distance},
                )
                to_email = notification_preference.user.email

                email = EmailMessage(
                    subject, message, settings.DEFAULT_FROM_EMAIL, [to_email]
                )
                email.send()

    # Po zakończeniu pętli zwracamy True, żeby poinformować o pomyślnym wysłaniu powiadomienia
    return True
