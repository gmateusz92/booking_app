from django.db import models
from booking import settings
# from django.contrib.gis.db import models as gis_models
# from django.contrib.gis.geos import Point

class Apartment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=20)
    description = models.CharField(null=True, max_length=1000)
    beds = models.IntegerField(null=True)
    capacity = models.IntegerField(null=True)
    price = models.IntegerField(null=True)
    # country = models.CharField(max_length=50, null=True)
    # city = models.CharField(max_length=50, null=True)
    # location = gis_models.PointField(null=True, blank=True)
    
    def __str__(self):
        return f'{self.name} with {self.beds} beds for {self.capacity} people'

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

    def __str__(self):
        return f'{self.user} has booked {self.name} from {self.check_in} to {self.check_out}'

#     def get_room_category(self): #funkcja pokazuje cala nazwe katerogii pokoju
#         room_categories = dict(self.room.ROOM_CATEGORIES)
#         room_category = room_categories.get(self.room.category)
#         return room_category

#     def get_cancel_booking_url(self):
#         pass
