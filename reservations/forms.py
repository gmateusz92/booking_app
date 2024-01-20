from django import forms
from .models import Apartment, Photo

class ApartmentForm(forms.ModelForm):
    class Meta:
        model = Apartment
        fields = ['name', 'description', 'beds', 'capacity', 'price']

class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['image']