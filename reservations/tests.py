from django.test import TestCase

from django.contrib.gis.geos import Point
from reservations.models import NotificationPreference
# Create your tests here.
def test_radius_units():
    # Tworzymy punkt dla lokalizacji użytkownika
    user_point = Point(0, 0)
    
    # Tworzymy przykładową preferencję powiadomień
    notification_preference = NotificationPreference.objects.create(
        latitude=0, 
        longitude=0, 
        radius=10  # Promień w kilometrach
    )
    
    # Sprawdzamy odległość dla różnych wartości
    distances_to_test = [5000, 15000]  # Odległości w metrach
    
    for distance in distances_to_test:
        # Sprawdzamy, czy odległość mieści się w zasięgu promienia
        if distance <= notification_preference.radius * 1000:  # Zamiana kilometrów na metry
            print(f"Odległość {distance} metrów: MIEŚCI SIĘ w promieniu {notification_preference.radius} kilometrów")
        else:
            print(f"Odległość {distance} metrów: NIE MIEŚCI SIĘ w promieniu {notification_preference.radius} kilometrów")