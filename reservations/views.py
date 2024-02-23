from django.shortcuts import render, redirect
from .models import Apartment, Booking, Photo, Message
from django.shortcuts import render, get_object_or_404
from .forms import ApartmentForm, PhotoForm, BookingForm, CommentForm
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from django.views.generic.edit import UpdateView
from django.db.models import Q
from django.conf import settings
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
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from datetime import date



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

    for apartment in apartments:
        average_rating = Booking.objects.filter(name=apartment).aggregate(Avg('rating'))['rating__avg']
        apartment.average_rating = round(average_rating, 2) if average_rating else None

    if query:
        keywords = query.split(', ')
        if len(keywords) >= 1:
            apartments = Apartment.objects.filter(
                Q(country__icontains=query) | Q(city__icontains=query) |
                Q(country__icontains=keywords[0]) | Q(city__icontains=keywords[0])
            )
            if len(keywords) >= 2:
                apartments = apartments.filter(Q(country__icontains=keywords[1]) & Q(city__icontains=keywords[0]))          
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
    

def apartment_list(request):
    user = request.user
    apartments = Apartment.objects.filter(user=user)
    return render(request, 'reservations/apartment_list.html', {'apartments': apartments})


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
    current_date = date.today()
    bookings = Booking.objects.filter(user=user, check_in__gte=current_date)
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
        d = get_date(self.request.GET.get('day', None))
        year, month = d.year, d.month
        prev_month = date(year, month, 1) - timedelta(days=1)
        prev_month_url = reverse('reservations:calendar') + f'?day={prev_month.year}-{prev_month.month}'
        next_month = date(year, month, 28) + timedelta(days=7)
        next_month_url = reverse('reservations:calendar') + f'?day={next_month.year}-{next_month.month}'
        
        cal = Calendar(year, month)

        html_cal = cal.formatmonth(withyear=True)
        context['calendar'] = mark_safe(html_cal)

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

def read_opinions(request, apartment_id):
    bookings = Booking.objects.filter(name_id=apartment_id).exclude(comment=None)
    return render(request, 'reservations/view_opinion.html', {'bookings': bookings})


# def booking_history(request):
#     form = CommentForm()
#     user_bookings = Booking.objects.filter(user=request.user, check_out__lt=datetime.now())
#     context = {
#         'user_bookings': user_bookings,
#         'form': form,
#     }
#     return render(request, 'reservations/booking_history.html', context)


# class BookingHistoryView(View):
#     template_name = 'reservations/booking_history.html'

#     def get(self, request, apartment_id):
#         apartment = get_object_or_404(Apartment, pk=apartment_id)
#         user_bookings = Booking.objects.filter(user=request.user, check_out__lt=datetime.now())
#         form = CommentForm()
#         context = {
#             'user_bookings': user_bookings,
#             'form': form,
#             'apartment': apartment,
#         }
#         return render(request, self.template_name, context)
    
#     def post(self, request, apartment_id, booking_id):
#         form = CommentForm(request.POST)

#         if form.is_valid():
#             comment = form.save(commit=False)
#             comment.user = request.user
#             comment.apartment = get_object_or_404(Apartment, pk=apartment_id)
#             comment.booking = get_object_or_404(Booking, pk=booking_id)
#             comment.save()
#             return redirect('reservations:BookingHistoryView', apartment_id=apartment_id)

#         return render(request, self.template_name, {'form': form })
    
def booking_history(request):
    current_datetime = date.today()
    bookings = Booking.objects.filter(user=request.user, check_out__lt=current_datetime)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            booking_id = form.cleaned_data['booking_id']
            comment_content = form.cleaned_data['comment']
            rating_value = form.cleaned_data['rating']
            booking = Booking.objects.get(id=booking_id)
            booking.comment = comment_content
            booking.rating = rating_value
            booking.save()
    else:
        form = CommentForm()
    return render(request, 'reservations/booking_history.html', {'bookings': bookings, 'form': form}) 