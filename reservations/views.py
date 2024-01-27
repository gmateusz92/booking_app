from django.shortcuts import render, redirect
from .models import Apartment, Booking, Photo
from django.shortcuts import render, get_object_or_404
from .forms import ApartmentForm, PhotoForm
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from django.views.generic.edit import UpdateView
from django.db.models import Q


# def home(request):
#     # Sprawdź, czy użytkownik wysłał formularz wyszukiwania
#     query = request.GET.get('q', '')
    
#     # Jeśli formularz został wysłany, szukaj w polu country i city
#     if query:
#         apartments = Apartment.objects.filter(
#             Q(country__icontains=query) | Q(city__icontains=query)
#         )
#     else:
#         # W przeciwnym razie, zwróć wszystkie apartamenty
#         apartments = Apartment.objects.all()

#     context = {
#         'apartments': apartments,
#     }
#     return render(request, 'home.html', context)

def home(request):
    # Sprawdź, czy użytkownik wysłał formularz wyszukiwania
    query = request.GET.get('q', '')

    # Sprawdź, czy użytkownik użył autouzupełnienia z Google Maps
    auto_complete_query = request.GET.get('id_address', '')

    # Użyj wartości z autouzupełnienia, jeśli jest dostępna
    query = auto_complete_query if auto_complete_query else query

    # Jeśli formularz został wysłany, szukaj w polu name, city, country
    if query:
        keywords = query.split(', ')
        if len(keywords) >= 1:
            apartments = Apartment.objects.filter(
                Q(country__icontains=query) | Q(city__icontains=query) |
                Q(country__icontains=keywords[0]) | Q(city__icontains=keywords[0])
            )
            if len(keywords) >= 2:
                apartments = apartments.filter(Q(country__icontains=keywords[1]) & Q(city__icontains=keywords[0]))
    else:
        # W przeciwnym razie, zwróć wszystkie apartamenty
        apartments = Apartment.objects.all()

    context = {
        'apartments': apartments,
    }
    return render(request, 'home.html', context)


# def home(request):
#     # Sprawdź, czy użytkownik wysłał formularz wyszukiwania
#     query = request.GET.get('q', '')

#     # Sprawdź, czy użytkownik użył autouzupełnienia z Google Maps
#     auto_complete_query = request.GET.get('id_address', '')

#     # Użyj wartości z autouzupełnienia, jeśli jest dostępna
#     query = auto_complete_query if auto_complete_query else query

#     # Jeśli formularz został wysłany, szukaj w polu name, city, country
#     if query:
#         keywords = query.split(', ')
        
#         # Sprawdź, czy fraza zawiera przecinek (czyli czy to wynik z Google Maps)
#         if ',' in query:
#             # Jeśli tak, użyj pierwszej części jako miasta, a drugiej jako kraju
#             city_conditions = Q(city__iexact=keywords[0].strip())
#             country_conditions = Q(country__iexact=keywords[1].strip())
#         else:
#             # W przeciwnym razie, traktuj całą frazę jako jeden warunek
#             city_conditions = Q(city__iexact=query)
#             country_conditions = Q(country__iexact=query)

#         # Połącz warunki dla kraju i miasta
#         apartments = Apartment.objects.filter(
#             Q(name__icontains=query) | Q(description__icontains=query) |
#             country_conditions | city_conditions
#         )
#     else:
#         # W przeciwnym razie, zwróć wszystkie apartamenty
#         apartments = Apartment.objects.all()

#     context = {
#         'apartments': apartments,
#     }
#     return render(request, 'home.html', context)





# def search(request):
#     query = request.GET.get('q')
#     if query:
#         # Wyszukaj apartamenty na podstawie wprowadzonego zapytania
#         apartments = Apartment.objects.filter(city__icontains=query)
#         # Dodaj więcej filtrów według potrzeb
#     else:
#         # Jeśli pasek wyszukiwania jest pusty, zwróć wszystkie apartamenty
#         apartments = Apartment.objects.all()

#     return render(request, 'reservations/search_location.html', {'apartments': apartments})


def apartment_detail(request, pk):
    apartment = get_object_or_404(Apartment, pk=pk)
    photo = Photo.objects.all()
    context = {
        'apartment': apartment,
        'photo': photo,
        }
    return render(request, 'reservations/apartment_detail.html', context)

# class MyApartmentView(LoginRequiredMixin, View):
#     template_name = 'reservations/my_apartments.html'

#     def get(self, request, *args, **kwargs):
#         my_apartments = Apartment.objects.filter(user=request.user)
#         context = {
#             'my_apartments': my_apartments
#             }
#         return render(request, self.template_name, context)
#<!-- <a class="nav-link" href="{% url 'reservations:MyApartmentView' pk=user.id %}">My Offers</a> -->

def apartment_list(request):
    user = request.user
    apartments = Apartment.objects.filter(user=user)
    return render(request, 'reservations/my_apartments.html', {'apartments': apartments})


        


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

# class EditApartmentView(View):
#     template_name = 'reservations/edit_apartment.html'

#     def get(self, request, pk):
#         apartment = get_object_or_404(Apartment, pk=pk)
#         form = ApartmentForm(instance=apartment)
#         return render(request, self.template_name, {'form': form, 'apartment': apartment})

#     def post(self, request, pk):
#         apartment = get_object_or_404(Apartment, pk=pk)
#         form = ApartmentForm(request.POST, instance=apartment)

#         if form.is_valid():
#             form.save()
#             return redirect('reservations:apartment_detail', pk=apartment.pk)

#         return render(request, self.template_name, {'form': form, 'apartment': apartment})


class EditApartmentView(View):
    template_name = 'reservations/edit_apartment.html'

    def get(self, request, pk):
        apartment = get_object_or_404(Apartment, pk=pk, user=request.user)
        form = ApartmentForm(instance=apartment)
        return render(request, self.template_name, {'form': form, 'apartment': apartment})

    def post(self, request, pk):
        apartment = get_object_or_404(Apartment, pk=pk, user=request.user)
        form = ApartmentForm(request.POST, instance=apartment)
        photo_form = PhotoForm(request.POST, request.FILES, instance=apartment.photos.first())

        if form.is_valid():
            apartment = form.save(commit=False)
            apartment.user = request.user
            apartment.save()

            # Dodatkowo obsługuje dodawanie zdjęcia
            
            if photo_form.is_valid():
                photo = photo_form.save(commit=False)
                photo.apartment = apartment
                photo.save()

            return redirect('reservations:apartment_detail', pk=apartment.pk)

        return render(request, self.template_name, {'form': form, 'apartment': apartment, 'photo_form': photo_form })


# def edit_apartment(request, apartment_id):
#     user = request.user
#     apartment = get_object_or_404(Apartment, id=apartment_id, user=user)

#     if request.method == 'POST':
#         apartment_form = ApartmentForm(request.POST, instance=apartment)
#         photo_form = PhotoForm(request.POST, request.FILES, instance=apartment.photos.first())

#         if apartment_form.is_valid() and photo_form.is_valid():
#             apartment = apartment_form.save(commit=False)
#             apartment.user = user
#             apartment.save()

#             # Obsługa dodawania zdjęcia
#             if 'image' in request.FILES:
#                 photo = photo_form.save(commit=False)
#                 photo.apartment = apartment
#                 photo.save()

#             return redirect('reservations:my_apartment_detail', apartment_id=apartment.id)
#     else:
#         apartment_form = ApartmentForm(instance=apartment)
#         photo_form = PhotoForm(instance=apartment.photos.first())

#     return render(request, 'reservations/edit_apartment.html', {
#         'apartment_form': apartment_form,
#         'photo_form': photo_form,
#         'apartment': apartment,
#     })   

class DeleteApartmentView(View):
    template_name = 'reservations/delete_apartment.html'

    def get(self, request, pk):
        apartment = get_object_or_404(Apartment, pk=pk)
        return render(request, self.template_name, {'apartment': apartment})

    def post(self, request, pk):
        apartment = get_object_or_404(Apartment, pk=pk)
        apartment.delete()
        if Apartment.objects.filter(user=request.user).exists():
            return redirect('reservations:apartment_list')
        else:
            # Jeśli użytkownik nie ma ofert, przekierowujemy na stronę główną
            return redirect('reservations:home')

def booking_list(request):
    bookings = Booking.objects.all()
    context = {
        'bookings': bookings
    }
    return render(request, 'reservations/bookinglist.html', context)

