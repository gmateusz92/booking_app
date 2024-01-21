from django import forms
from .models import Apartment, Photo

class ApartmentForm(forms.ModelForm):
    class Meta:
        model = Apartment
        fields = ['name', 'description', 'beds', 'capacity', 'price']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control narrow-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control narrow-input'}),
            'beds': forms.NumberInput(attrs={'class': 'form-control narrow-input'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control narrow-input'}),
            'price': forms.NumberInput(attrs={'class': 'form-control narrow-input'}),
        }

class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control narrow-input'}),
        }