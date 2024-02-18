from django.shortcuts import render, redirect
from .models import Apartment, Booking, Photo, Message, Booking_notification
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
from django.core.mail import send_mail
from .utils import get_date
from accounts.utils import send_verification_email



def map(request):
    reservation_form = BookingForm()  # Inicjalizuj formularz rezerwacji

    context = {
        'reservation_form': reservation_form,  # Dodaj formularz do kontekstu
        # 'google_maps_api_key': 'AIzaSyDpgf2CtlTEoJaQWnxVWi1KMwo7zb2APqc',  # Zastąp kluczem API
    }
    return render(request, 'reservations/map.html', context)


def home(request):
    query = request.GET.get('q', '')
    auto_complete_query = request.GET.get('id_address', '')
    query = auto_complete_query if auto_complete_query else query
    
    sort_by_price = request.GET.get('sort_by_price')
    apartments = Apartment.objects.all()


    if query:
        keywords = query.split(', ')
        if len(keywords) >= 1:
            apartments = Apartment.objects.filter(
                Q(country__icontains=query) | Q(city__icontains=query) |
                Q(country__icontains=keywords[0]) | Q(city__icontains=keywords[0])
            )
            if len(keywords) >= 2:
                apartments = apartments.filter(Q(country__icontains=keywords[1]) & Q(city__icontains=keywords[0]))
    # else:
    #     apartments = Apartment.objects.all()
                
    if sort_by_price == 'asc':
        apartments = apartments.order_by('price')
    elif sort_by_price == 'desc':
        apartments = apartments.order_by('-price')            

    context = {
        'apartments': apartments,
    }
    return render(request, 'home.html', context)


class ApartmentDetailView(View):
    template_name = 'reservations/apartment_detail.html'

    def get(self, request, pk):
        apartment = get_object_or_404(Apartment, pk=pk)
        photo = Photo.objects.all()
        apartments = Apartment.objects.all()

        d = get_date(request.GET.get('day', None))
        year, month = d.year, d.month
        prev_month = date(year, month, 1) - timedelta(days=1)
        prev_month_url = reverse('reservations:calendar') + f'?day={prev_month.year}-{prev_month.month}'
        next_month = date(year, month, 28) + timedelta(days=7)
        next_month_url = reverse('reservations:calendar') + f'?day={next_month.year}-{next_month.month}'

        cal = Calendar(year, month, apartment)
        html_cal = cal.formatmonth(withyear=True)

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



# def get_date(req_day):
#         if req_day:
#             year, month = (int(x) for x in req_day.split('-'))
#             return date(year, month, day=1)
#         return datetime.today()  


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

            #  # Wysyłanie wiadomości e-mailowej do użytkownika
            # user_subject = 'Potwierdzenie Twojej rezerwacji'
            # user_message = f'Witaj {request.user.username},\n\nTwoja rezerwacja dla {apartment.name} została potwierdzona.'
            # user_recipient_email = request.user.email
            # send_mail(user_subject, user_message, None, [user_recipient_email])

            # # Wysyłanie wiadomości e-mailowej do właściciela apartamentu
            # owner_subject = 'Nowa rezerwacja dla Twojego apartamentu'
            # owner_message = f'Właśnie dokonano nowej rezerwacji dla Twojego apartamentu {apartment.name}.'
            # owner_recipient_email = apartment.user.email
            # send_mail(owner_subject, owner_message, None, [owner_recipient_email])
            # send verification email
            user = apartment.user
            mail_subject = 'You have new reservation!'
            email_template = 'emails/reservation_done.html'
            send_verification_email(request, user, mail_subject, email_template)

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

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Booking, Message

@login_required
def message_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    apartment = booking.name
    if request.method == 'POST':
        content = request.POST.get('content')
        sender = request.user
        receiver = apartment.user
        Message.objects.create(sender=sender, receiver=receiver, booking=booking, content=content)
        # Optional: Add logic to handle message creation and redirection after sending
    messages = Message.objects.filter(booking=booking)
    return render(request, 'reservations/message.html', {'booking': booking, 'apartment': apartment, 'messages': messages})

@login_required
def message_list(request):
    user=request.user
    bookings = Booking.objects.filter(user=user)
    messages = Message.objects.filter(sender=user) | Message.objects.filter(receiver=user)
    context = {
        'bookings': bookings,
        'messages': messages,
    }
    return render(request, 'reservations/all_messages.html', context)


