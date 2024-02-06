from django.shortcuts import render, redirect
from .models import Apartment, Booking, Photo, Message
from django.shortcuts import render, get_object_or_404
from .forms import ApartmentForm, PhotoForm, BookingForm
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from django.views.generic.edit import UpdateView
from django.db.models import Q
from django.conf import settings
import googlemaps
from datetime import datetime, date, timedelta
from django.utils.safestring import mark_safe
from .models import *
from .utils import Calendar
from django.views.generic import ListView
from django.urls import reverse
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required



def map(request):
    reservation_form = BookingForm()  # Inicjalizuj formularz rezerwacji

    context = {
        'reservation_form': reservation_form,  # Dodaj formularz do kontekstu
        # 'google_maps_api_key': 'AIzaSyDpgf2CtlTEoJaQWnxVWi1KMwo7zb2APqc',  # Zastąp kluczem API
    }
    return render(request, 'reservations/map.html', context)


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

# class ApartmentDetailView(DetailView):
#     model = Apartment
#     template_name = 'reservations/apartment_detail.html'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)

#         # Pobieramy obiekt daty na podstawie parametru 'day' z żądania
#         d = get_date(self.request.GET.get('day', None))

#         # Ustalamy aktualny rok i miesiąc
#         year, month = d.year, d.month

#         # Przechodzimy do poprzedniego miesiąca
#         prev_month = date(year, month, 1) - timedelta(days=1)
#         prev_month_url = reverse('reservations:calendar') + f'?day={prev_month.year}-{prev_month.month}'

#         # Przechodzimy do następnego miesiąca
#         next_month = date(year, month, 28) + timedelta(days=7)
#         next_month_url = reverse('reservations:calendar') + f'?day={next_month.year}-{next_month.month}'

#         # Instantiate our calendar class with today's year and date
#         cal = Calendar(year, month)

#         # Call the formatmonth method, which returns our calendar as a table
#         html_cal = cal.formatmonth(withyear=True)
#         context['calendar'] = mark_safe(html_cal)

#         # Dodajemy dane nawigacyjne do kontekstu
#         context['prev_month_url'] = prev_month_url
#         context['next_month_url'] = next_month_url

#         return context


# def apartment_detail(request, pk):
#     apartment = get_object_or_404(Apartment, pk=pk)
#     photo = Photo.objects.all()
#     apartments = Apartment.objects.all()
#     context = {
#         'apartment': apartment,
#         'photo': photo,
#         'apartments': apartments,
        
#         }
#     return render(request, 'reservations/xx.html', context)


class ApartmentDetailView(View):
    template_name = 'reservations/apartment_detail.html'

    def get(self, request, pk):
        apartment = get_object_or_404(Apartment, pk=pk)
        photo = Photo.objects.all()
        apartments = Apartment.objects.all()

        # Dodaj kod dla kalendarza
        d = get_date(request.GET.get('day', None))
        year, month = d.year, d.month
        prev_month = date(year, month, 1) - timedelta(days=1)
        prev_month_url = reverse('reservations:calendar') + f'?day={prev_month.year}-{prev_month.month}'
        next_month = date(year, month, 28) + timedelta(days=7)
        next_month_url = reverse('reservations:calendar') + f'?day={next_month.year}-{next_month.month}'

        
        
        cal = Calendar(year, month, apartment)
        html_cal = cal.formatmonth(withyear=True)




        # cal = Calendar(year, month)
        # html_cal = cal.formatmonth(withyear=True)

        context = {
            'apartment': apartment,
            'photo': photo,
            'apartments': apartments,
            'calendar': mark_safe(html_cal),
            'prev_month_url': prev_month_url,
            'next_month_url': next_month_url,
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
            return redirect('reservations:ApartmentDetailView', pk=apartment.pk)

        return render(request, self.template_name, {'form': form, 'photo_form': photo_form})    


class EditApartmentView(View):
    template_name = 'reservations/edit_apartment.html'

    
    
    def get(self, request, pk):
        apartment = get_object_or_404(Apartment, pk=pk, user=request.user)
        form = ApartmentForm(instance=apartment)
        photo_form = PhotoForm(instance=apartment.photos.first())
        return render(request, self.template_name, {'form': form, 'apartment': apartment, 'photo_form': photo_form})

    def post(self, request, pk):
        apartment = get_object_or_404(Apartment, pk=pk, user=request.user)
        form = ApartmentForm(request.POST, instance=apartment)
        photo_form = PhotoForm(request.POST, request.FILES)

        if form.is_valid() and photo_form.is_valid():
            apartment = form.save(commit=False)
            apartment.user = request.user
            apartment.save()

            photo = photo_form.save(commit=False)
            photo.apartment = apartment
            photo.save()

            return redirect('reservations:ApartmentDetailView', pk=apartment.pk)

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

@login_required
def booking_list(request):
    user=request.user
    bookings = Booking.objects.filter(user=user)
    context = {
        'bookings': bookings
    }
    return render(request, 'reservations/bookinglist.html', context)



def get_date(req_day):
        if req_day:
            year, month = (int(x) for x in req_day.split('-'))
            return date(year, month, day=1)
        return datetime.today()  


class CalendarView(ListView):
    model = Booking
    template_name = 'reservations/calendar.html'
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Pobieramy obiekt daty na podstawie parametru 'day' z żądania
        d = get_date(self.request.GET.get('day', None))

        # Ustalamy aktualny rok i miesiąc
        year, month = d.year, d.month

        # Przechodzimy do poprzedniego miesiąca
        prev_month = date(year, month, 1) - timedelta(days=1)
        prev_month_url = reverse('reservations:calendar') + f'?day={prev_month.year}-{prev_month.month}'

        # Przechodzimy do następnego miesiąca
        next_month = date(year, month, 28) + timedelta(days=7)
        next_month_url = reverse('reservations:calendar') + f'?day={next_month.year}-{next_month.month}'

        # Instantiate our calendar class with today's year and date
        cal = Calendar(year, month)

        # Call the formatmonth method, which returns our calendar as a table
        html_cal = cal.formatmonth(withyear=True)
        context['calendar'] = mark_safe(html_cal)

        # Dodajemy dane nawigacyjne do kontekstu
        context['prev_month_url'] = prev_month_url
        context['next_month_url'] = next_month_url

        return context
    
   
# class CalendarView(View):
#     template_name = 'reservations/calendar.html'

#     def get(self, request, pk, year, month):
#         apartment = get_object_or_404(Apartment, pk=pk)
#         photo = Photo.objects.all()
#         apartments = Apartment.objects.all()

#         # Oblicz poprzedni i kolejny miesiąc
#         prev_month = date(year, month, 1) - timedelta(days=1)
#         next_month = date(year, month, 28) + timedelta(days=7)

#         # Twórz linki do poprzedniego i kolejnego miesiąca z uwzględnieniem apartamentu
#         prev_month_url = reverse('reservations:calendar', args=[pk, prev_month.year, prev_month.month])
#         next_month_url = reverse('reservations:calendar', args=[pk, next_month.year, next_month.month])

#         # Twórz kalendarz
#         cal = Calendar(year, month, apartment)
#         html_cal = cal.formatmonth(withyear=True)

#         context = {
#             'apartment': apartment,
#             'photo': photo,
#             'apartments': apartments,
#             'calendar': mark_safe(html_cal),
#             'prev_month_url': prev_month_url,
#             'next_month_url': next_month_url,
#         }

#         return render(request, 'reservations/calendar.html', context)
    

# class ReserveView(View):
#     template_name = 'reservations/reserve_apartment.html'

#     def get(self, request, pk):
#         apartment = get_object_or_404(Apartment, pk=pk)

#         d = get_date(request.GET.get('day', None))
#         year, month = d.year, d.month
#         prev_month = date(year, month, 1) - timedelta(days=1)
#         prev_month_url = reverse('reservations:ReserveView', kwargs={'pk': pk}) + f'?day={prev_month.year}-{prev_month.month}'
#         next_month = date(year, month, 28) + timedelta(days=7)
#         next_month_url = reverse('reservations:ReserveView', kwargs={'pk': pk}) + f'?day={next_month.year}-{next_month.month}'

#         cal = Calendar(year, month, apartment)
#         html_cal = cal.formatmonth(withyear=True)

#         context = {
#             'apartment': apartment,
#             'calendar': mark_safe(html_cal),
#             'prev_month_url': prev_month_url,
#             'next_month_url': next_month_url,
#         }

#         return render(request, self.template_name, context)
    
#     def post(self, request):
#         form = ReservationForm(request.POST)
        

#         if form.is_valid():
#             booking = form.save(commit=False)
#             booking.user=request.user
#             booking.save()
            
#             return redirect('reservations:booking_list', pk=booking.pk)
        
#         return render(request, self.template_name, {'form': form, 'booking': booking })
    


class BookingView(View):
    template_name = 'reservations/reserve_apartment.html'

    def get(self, request, pk):
        apartment = get_object_or_404(Apartment, pk=pk)

        d = get_date(request.GET.get('day', None))
        year, month = d.year, d.month
        prev_month = date(year, month, 1) - timedelta(days=1)
        prev_month_url = reverse('reservations:BookingView', kwargs={'pk': pk}) + f'?day={prev_month.year}-{prev_month.month}'
        next_month = date(year, month, 28) + timedelta(days=7)
        next_month_url = reverse('reservations:BookingView', kwargs={'pk': pk}) + f'?day={next_month.year}-{next_month.month}'

        cal = Calendar(year, month, apartment)
        html_cal = cal.formatmonth(withyear=True)
        form = BookingForm(initial={'name': apartment.id})  # Ustawia wartość ukrytego pola

        context = {
            'apartment': apartment,
            'calendar': mark_safe(html_cal),
            'prev_month_url': prev_month_url,
            'next_month_url': next_month_url,
            'form': form,  # Dodaj formularz do kontekstu widoku
        }

        return render(request, self.template_name, context)
    
    def post(self, request, pk):
        apartment = get_object_or_404(Apartment, pk=pk)
        form = BookingForm(request.POST)

        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.apartment = apartment  # Dodaj przypisanie apartamentu do rezerwacji
            booking.save()
            return redirect('reservations:booking_list')
        else:
            # form.errors.clear()
            messages.error(request, form.errors['check_in'])
        
        d = get_date(request.GET.get('day', None))
        year, month = d.year, d.month
        prev_month = date(year, month, 1) - timedelta(days=1)
        prev_month_url = reverse('reservations:BookingView', kwargs={'pk': pk}) + f'?day={prev_month.year}-{prev_month.month}'
        next_month = date(year, month, 28) + timedelta(days=7)
        next_month_url = reverse('reservations:BookingView', kwargs={'pk': pk}) + f'?day={next_month.year}-{next_month.month}'

        cal = Calendar(year, month, apartment)
        html_cal = cal.formatmonth(withyear=True)

        context = {
            'apartment': apartment,
            'calendar': mark_safe(html_cal),
            'prev_month_url': prev_month_url,
            'next_month_url': next_month_url,
            'form': form,
        }

        return render(request, self.template_name, context)


class DeleteBookingView(View):
    template_name = 'reservations/delete_booking.html'

    def get(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk)
        return render(request, self.template_name, {'booking': booking})

    def post(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk)
        booking.delete()
        if Booking.objects.filter(user=request.user).exists():
            return redirect('reservations:booking_list')
        else:
            # Jeśli użytkownik nie ma rezerwacji, przekierowujemy na stronę główną
            return redirect('reservations:home')
        

# def czat(request, pk):
#     apartment = get_object_or_404(Apartment, id=pk)
#     owner = apartment.user
#     booking = get_object_or_404(Booking, user=request.user, name=apartment)

#     if request.method == 'POST':
#         text = request.POST.get('text')
#         message = Message.objects.create(sender=request.user, receiver=owner, text=text)
#         return JsonResponse({'status': 'ok'})

#     messages = Message.objects.filter(
#         (models.Q(nadawca=request.user, odbiorca=owner)) | (models.Q(nadawca=owner, odbiorca=request.user))
#     ).order_by('data')

#     return render(request, 'czat.html', {'wlasciciel_apartamentu': owner, 'wiadomosci': messages, 'booking': booking})        

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Apartment, Booking, Message

def czat(request, pk):
    apartment = get_object_or_404(Apartment, pk=pk)
    owner = apartment.user
    booking = None

    try:
        booking = Booking.objects.get(user=request.user, name=apartment)
    except Booking.DoesNotExist:
        pass
    except Booking.MultipleObjectsReturned:
        booking = Booking.objects.filter(user=request.user, name=apartment).first()

    if request.method == 'POST':
        text = request.POST.get('text')
        if text:
            message = Message.objects.create(sender=request.user, receiver=owner, text=text)
            return redirect('reservations:czat', pk=pk)
            #return JsonResponse({'status': 'ok'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Text field is empty'})

    messages = Message.objects.filter(
        (models.Q(sender=request.user, receiver=owner)) | (models.Q(sender=owner, receiver=request.user))
    ).order_by('date')

    return render(request, 'reservations/czat.html', {'owner': owner, 'messages': messages, 'booking': booking})
