from django.shortcuts import render, redirect
from .models import Apartment, Booking, Photo
from django.shortcuts import render, get_object_or_404
from .forms import ApartmentForm, PhotoForm
from django.views import View

# Create your views here.
def home(request):
    apartments = Apartment.objects.all()
    context = {
        'apartments' : apartments,
    }
    return render(request, 'home.html', context)

def apartment_detail(request, pk):
    apartment = get_object_or_404(Apartment, pk=pk)
    photo = Photo.objects.all()
    context = {
        'apartment': apartment,
        'photo': photo,
        }
    return render(request, 'reservations/apartment_detail.html', context)

# def add_apartment(request):
#     if request.method == 'POST':
#         apartment_form = ApartmentForm(request.POST)
#         photo_form = PhotoForm(request.POST, request.FILES)
        
#         if apartment_form.is_valid() and photo_form.is_valid():
#             apartment = apartment_form.save()
#             photo = photo_form.save(commit=False)
#             photo.apartment = apartment
#             photo.save()
#             return redirect('reservations:apartment_detail', pk=apartment.pk)
#     else:
#         apartment_form = ApartmentForm()
#         photo_form = PhotoForm()
    
#     return render(request, 'reservations/add_apartment.html', {'apartment_form': apartment_form, 'photo_form': photo_form})

class AddApartmentView(View):
    template_name = 'reservations/add_apartment.html'

    def get(self, request):
        form = ApartmentForm()
        photo_form = PhotoForm()
        return render(request, self.template_name, {'form': form, 'photo_form': photo_form})

    def post(self, request):
        form = ApartmentForm(request.POST)
        photo_form = PhotoForm(request.POST, request.FILES)

        if form.is_valid() and photo_form.is_valid():
            apartment = form.save(commit=False)
            apartment.user=request.user
            apartment.save()

            photo = photo_form.save(commit=False)
            photo.apartment = apartment
            photo.save()
            
            return redirect('reservations:apartment_detail', pk=apartment.pk)

        return render(request, self.template_name, {'form': form, 'photo_form': photo_form})    

class EditApartmentView(View):
    template_name = 'reservations/edit_apartment.html'

    def get(self, request, pk):
        apartment = get_object_or_404(Apartment, pk=pk)
        form = ApartmentForm(instance=apartment)
        return render(request, self.template_name, {'form': form, 'apartment': apartment})

    def post(self, request, pk):
        apartment = get_object_or_404(Apartment, pk=pk)
        form = ApartmentForm(request.POST, instance=apartment)

        if form.is_valid():
            form.save()
            return redirect('reservations:apartment_detail', pk=apartment.pk)

        return render(request, self.template_name, {'form': form, 'apartment': apartment})

class DeleteApartmentView(View):
    template_name = 'reservations/delete_apartment.html'

    def get(self, request, pk):
        apartment = get_object_or_404(Apartment, pk=pk)
        return render(request, self.template_name, {'apartment': apartment})

    def post(self, request, pk):
        apartment = get_object_or_404(Apartment, pk=pk)
        apartment.delete()
        return redirect('reservations:apartment_detail')  # Zastąp 'nazwa_twojego_widoku_listy' odpowiednią nazwą


def booking_list(request):
    bookings = Booking.objects.all()
    context = {
        'bookings': bookings
    }
    return render(request, 'reservations/bookinglist.html', context)