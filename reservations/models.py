from django.db import models

class Room(models.Model):
   
    name = models.CharField(max_length=20)
    beds = models.IntegerField(null=True)
    capacity = models.CharField(max_length=100, null=True)

    def __str__(self):
        return f'{self.name} with {self.beds} beds for {self.capacity} people'



# class Booking(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
#     room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True)
#     check_in = models.DateTimeField(null=True)
#     check_out = models.DateTimeField(null=True)

#     def __str__(self):
#         return f'{self.user} has booked {self.room} from {self.check_in} to {self.check_out}'

#     def get_room_category(self): #funkcja pokazuje cala nazwe katerogii pokoju
#         room_categories = dict(self.room.ROOM_CATEGORIES)
#         room_category = room_categories.get(self.room.category)
#         return room_category

#     def get_cancel_booking_url(self):
#         pass
