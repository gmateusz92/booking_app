from django import forms
from .models import Apartment, Photo, Booking #, Comment
from django.core.exceptions import ValidationError
from django.contrib import messages
from multiupload.fields import MultiFileField

class ApartmentForm(forms.ModelForm):
    class Meta:
        model = Apartment
        fields = ['name', 'description', 'beds', 'capacity', 'price', 'address', 'country', 'city', 'latitude', 'longitude', 'location']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control narrow-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control narrow-input'}),
            'beds': forms.NumberInput(attrs={'class': 'form-control narrow-input'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control narrow-input'}),
            'price': forms.NumberInput(attrs={'class': 'form-control narrow-input'}),
            'address': forms.TextInput(attrs={'class': 'form-control narrow-input'}),
            'country': forms.TextInput(attrs={'class': 'form-control narrow-input'}),
            'city': forms.TextInput(attrs={'class': 'form-control narrow-input'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control narrow-input'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control narrow-input'}),
            'location': forms.NumberInput(attrs={'class': 'form-control narrow-input'}),     
        }

class PhotoForm(forms.ModelForm):
    image = MultiFileField(max_num=8, min_num=1, max_file_size=1024*1024*5)
    class Meta:
        model = Photo
        fields = ['image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control narrow-input'}),
        }

# class ReservationForm(forms.ModelForm):
#     class Meta:
#         model = Booking
#         fields = [ 'check_in', 'check_out', 'name']

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['check_in', 'check_out', 'name']
        widgets = {
            'check_in': forms.DateInput(attrs={'class': 'form-control narrow-input', 'type': 'date'}),
            'check_out': forms.DateInput(attrs={'class': 'form-control narrow-input', 'type': 'date'}),
            'name': forms.HiddenInput(attrs={'required': False})
        }
    # def clean(self):
    #     cleaned_data = super().clean()
    #     check_in = cleaned_data.get('check_in')
    #     check_out = cleaned_data.get('check_out')
    #     name = cleaned_data.get('name')

    #     if check_in and check_out and name:
    #         # Sprawdź, czy istnieje inna rezerwacja w tym terminie dla tego samego apartamentu
    #         overlapping_bookings = Booking.objects.filter(
    #             name=name,
    #             check_out__gt=check_in,
    #             check_in__lt=check_out
    #         )

    #         if overlapping_bookings.exists():
                
    #             # self.add_error(None, "This apartment is already booked for the selected dates.")
    #             # raise ValidationError({'__all__': 'This apartment is already booked for the selected dates.'})
    #             raise forms.ValidationError("This apartment is already booked for the selected datesss.")
            
    #     return cleaned_data
    
# class CommentForm(forms.ModelForm):
#     class Meta:
#         model = Comment
#         fields = ['content']

from django.core.validators import MinValueValidator, MaxValueValidator

class CommentForm(forms.Form):
    booking_id = forms.IntegerField(widget=forms.HiddenInput())
    comment = forms.CharField(widget=forms.Textarea)
    rating = forms.IntegerField(label='Rating (1-5)', validators=[MinValueValidator(1), MaxValueValidator(5)])

# class CommentForm(forms.ModelForm):
#     booking_id = forms.IntegerField(widget=forms.HiddenInput())
#     class Meta:
#         model = Booking
#         fields = [ 'comment', 'rating', 'booking_id']



from .models import NotificationPreference

class NotificationPreferenceForm(forms.ModelForm):
    class Meta:
        model = NotificationPreference
        fields = ['address', 'country', 'city', 'latitude','longitude', 'radius', ]
        widgets = {
            
            'radius': forms.NumberInput(attrs={'class': 'form-control narrow-input'}),
            'address': forms.TextInput(attrs={'class': 'form-control narrow-input'}),
            'country': forms.TextInput(attrs={'class': 'form-control narrow-input'}),
            'city': forms.TextInput(attrs={'class': 'form-control narrow-input'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control narrow-input'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control narrow-input'}),
            'location': forms.NumberInput(attrs={'class': 'form-control narrow-input'}),
            
        }
        