from django.db import models
from booking import settings
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Point
from django_google_maps import fields as map_fields
from django.urls import reverse

class Apartment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=20)
    description = models.CharField(null=True, max_length=1000)
    beds = models.IntegerField(null=True)
    capacity = models.IntegerField(null=True)
    price = models.IntegerField(null=True)
    address = models.CharField(max_length=250, blank=True, null=True)
    country = models.CharField(max_length=50, null=True)
    city = models.CharField(max_length=50, null=True)
    latitude = models.FloatField(max_length=20, blank=True, null=True)
    longitude = models.FloatField(max_length=20, blank=True, null=True)
    location = gis_models.PointField(null=True, blank=True, srid=4326)
    geolocation = map_fields.GeoLocationField(max_length=100, null=True)
    
    def __str__(self):
        return f'{self.name}'
    
    def save(self, *args, **kwargs):
        if self.latitude and self.longitude:
            self.location = Point(float(self.longitude), float(self.latitude))
            return super(Apartment, self).save(*args, **kwargs)
        return super(Apartment, self).save(*args, **kwargs)
    
    def get_absolute_url(self):
        # Zwraca URL do widoku detali apartamentu.
        return reverse('reservations:ApartmentDetailView', kwargs={'pk': self.pk})

class Photo(models.Model):
    apartment = models.ForeignKey(Apartment, related_name='photos', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='static/images/', null=True, blank=True)
    
    def __str__(self):
        return f'{self.image} '


class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    name = models.ForeignKey(Apartment, on_delete=models.CASCADE, null=True)
    check_in = models.DateTimeField(null=True)
    check_out = models.DateTimeField(null=True)
    comment = models.TextField(blank=True, null=True)
    rating = models.IntegerField(blank=True, null=True)

    def __str__(self):
        formatted_check_in = self.check_in.strftime('%d-%m-%Y')
        formatted_check_out = self.check_out.strftime('%d-%m-%Y')
        return f'{self.name} booked from {formatted_check_in} to {formatted_check_out}'


class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Message from {self.sender} to {self.receiver} regarding booking of {self.booking.name} from {self.booking.check_in.strftime('%d-%m-%Y')} to {self.booking.check_out.strftime('%d-%m-%Y')}"
    

class NotificationPreference(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    address = models.CharField(max_length=250, blank=True, null=True)
    country = models.CharField(max_length=50, null=True)
    city = models.CharField(max_length=50, null=True)
    latitude = models.FloatField(max_length=20, blank=True, null=True)
    longitude = models.FloatField(max_length=20, blank=True, null=True)
    location = gis_models.PointField(null=True, blank=True, srid=4326)  
    geolocation = map_fields.GeoLocationField(max_length=100, null=True)
    radius = models.PositiveIntegerField(default=0)     

    def save(self, *args, **kwargs):
        if self.latitude and self.longitude:
            self.location = Point(float(self.longitude), float(self.latitude))
            return super(NotificationPreference, self).save(*args, **kwargs)
        return super(NotificationPreference, self).save(*args, **kwargs)

    def __str__(self):
        return f"Powiadomienia dla {self.user.username}"