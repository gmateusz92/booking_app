from django.contrib import admin
from django_google_maps import fields as map_fields
from django_google_maps import widgets as map_widgets

from .models import Apartment, Booking, Message, NotificationPreference, Photo

admin.site.register(Apartment)
admin.site.register(Booking)
admin.site.register(Photo)
admin.site.register(Message)
admin.site.register(NotificationPreference)


class RentalAdmin(admin.ModelAdmin):
    formfield_overrides = {
        map_fields.AddressField: {"widget": map_widgets.GoogleMapsAddressWidget},
    }
