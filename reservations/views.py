from django.shortcuts import render, redirect
from .models import Apartment, Booking, Photo, Message
from django.shortcuts import render, get_object_or_404
from .forms import ApartmentForm, PhotoForm, BookingForm, CommentForm
from django.views import View
from django.db.models import Q
from datetime import date, timedelta
from django.utils.safestring import mark_safe
from .models import *
from .utils import Calendar
from django.views.generic import ListView
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .utils import get_date
from accounts.utils import send_verification_email, send_notification
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Avg
from datetime import date
from django.core.mail import send_mail
from django.template.loader import render_to_string


def home(request):
    query = request.GET.get('q', '')
    auto_complete_query = request.GET.get('id_address', '')
    query = auto_complete_query if auto_complete_query else query
    sort_by_price = request.GET.get('sort_by_price')
    apartments = Apartment.objects.all()

    for apartment in apartments:
        average_rating = Booking.objects.filter(name=apartment).aggregate(Avg('rating'))['rating__avg']
        if average_rating is not None:
            apartment.average_rating = round(average_rating, 2)
        else:
            apartment.average_rating = "No Ratings"

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
    
@login_required
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

            check_location(apartment.pk)
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
 
@login_required 
def vendor_booking_list(request):
    user = request.user
    current_date = date.today()
    user_apartments = Apartment.objects.filter(user=user)
 
    owner_bookings = []
    for apartment in user_apartments:
        bookings = Booking.objects.filter(name=apartment, check_in__gte=current_date)
        owner_bookings.extend(bookings)
    
    context = {
        'bookings': owner_bookings
    }
    return render(request, 'reservations/vendor_booking_list.html', context)

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
     
from django.utils.translation import gettext as _

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
        form = BookingForm(initial={'name': apartment.id}) 

        context = {
            'apartment': apartment,
            'calendar': mark_safe(html_cal),
            'prev_month_url': prev_month_url,
            'next_month_url': next_month_url,
            'form': form, 
        }

        return render(request, self.template_name, context)
    
    def post(self, request, pk):
        apartment = get_object_or_404(Apartment, pk=pk)
        form = BookingForm(request.POST)

        if form.is_valid():
            check_in = form.cleaned_data['check_in']
            check_out = form.cleaned_data['check_out']
            
            # Sprawdzenie, czy nowa rezerwacja nakłada się na istniejące
            overlapping_bookings = Booking.objects.filter(
                Q(check_out__gt=check_in, check_in__lt=check_out) |  # zarezerwowany przed wyjazdem lub po zameldowaniu
                Q(check_in__lt=check_out, check_out__gt=check_in),  # wyjazd zameldowano przed zameldowaniem lub po zameldowaniu
                name=apartment  # pole identyfikujące apartament w modelu Booking
            )
            if overlapping_bookings.exists():
                messages.error(request, _("This apartment is already booked for the selected dates."))
            elif Booking.objects.filter(check_in=check_out).exists() or Booking.objects.filter(check_out=check_in).exists():
                messages.error(request, _("This apartment is already booked for the selected dates."))
            else:
                # Tworzenie nowej rezerwacji
                booking = form.save(commit=False)
                booking.user = request.user
                booking.name = apartment  # przypisanie apartamentu do rezerwacji
                booking.save()
                user = apartment.user
                mail_subject = _('You have a new reservation!')
                email_template = 'emails/reservation_done.html'
                send_verification_email(request, user, mail_subject, email_template)
                return redirect('reservations:booking_list')
            
            
        
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


from django.db.models import Q


@login_required
def message_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    apartment = booking.name
    if request.method == 'POST':
        content = request.POST.get('content')
        sender = request.user
        receiver = booking.user
        message = Message.objects.create(sender=sender, receiver=receiver, booking=booking, content=content)
        if sender == apartment.user:
            subject = 'You have a new message.'
            template = 'emails/new_message.html'
            context = {'message': message}
            html_message = render_to_string(template, context)
            send_mail(subject, '', None, [receiver.email], html_message=html_message)
        else:  # Użytkownik rezerwujący wysyła wiadomość
            subject = 'You have a new message.'
            template = 'emails/new_message.html'
            context = {'message': message}
            html_message = render_to_string(template, context)
            send_mail(subject, '', None, [apartment.user.email], html_message=html_message)

    messages = Message.objects.filter(booking=booking)
    return render(request, 'reservations/message.html', {'booking': booking, 'apartment': apartment, 'messages': messages})



def read_opinions(request, apartment_id):
    bookings = Booking.objects.filter(name_id=apartment_id).exclude(comment=None)
    return render(request, 'reservations/view_opinion.html', {'bookings': bookings})


@login_required    
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


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import NotificationPreference
from .forms import NotificationPreferenceForm

# @login_required
# def notification_preference(request):
#     notification_pref, created = NotificationPreference.objects.get_or_create(user=request.user)
#     if request.method == 'POST':
#         form = NotificationPreferenceForm(request.POST, instance=notification_pref)
#         if form.is_valid():
#             form.save()
#             return redirect('reservations:notification_preference')
#     else:
#         form = NotificationPreferenceForm(instance=notification_pref)
#     return render(request, 'reservations/notification_preference.html', {'form': form})

class AddNotificationPreferenceView(View):
    template_name = 'reservations/notification_preference.html'

    def get(self, request):
        preferences = NotificationPreference.objects.all()
        form = NotificationPreferenceForm()
        return render(request, self.template_name, {'form': form, 'preferences': preferences })
    
    def post(self, request):
        form = NotificationPreferenceForm(request.POST)

        if form.is_valid():
            notification = form.save(commit=False)
            notification.user=request.user
            notification.save()
            return redirect('reservations:AddNotificationPreferenceView')

        return render(request, self.template_name, {'form': form})

from django.core.mail import EmailMessage
from django.contrib.gis.measure import Distance
from geopy.distance import geodesic
from django.contrib.gis.geos import Point

def check_location(pk):
    # Pobieramy nowo dodany apartament o podanym identyfikatorze (pk)
    apartment = Apartment.objects.get(pk=pk)
    
    for notification_preference in NotificationPreference.objects.all():
        # Sprawdzamy czy oba obiekty mają ustawione współrzędne
        if notification_preference.location is not None and apartment.location is not None:
            # Tworzymy punkt dla lokalizacji apartamentu i lokalizacji użytkownika
            apartment_point = apartment.location
            user_point = notification_preference.location
            print(apartment_point, user_point)
            # Obliczamy odległość między lokalizacją apartamentu a lokalizacją użytkownika
            distance = geodesic((user_point.y, user_point.x), (apartment_point.y, apartment_point.x)).kilometers
            print(distance)
            # Sprawdzamy czy odległość jest mniejsza lub równa radiusowi z NotificationPreference
            if distance <= notification_preference.radius:
                # Wysyłamy powiadomienie e-mail
                subject = 'Nowy apartament w pobliżu'
                message = render_to_string('emails/notification_email.html', {'apartment': apartment, 'distance': distance})
                to_email = notification_preference.user.email

                email = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, [to_email])
                email.send()
    
    # Po zakończeniu pętli zwracamy True, żeby poinformować o pomyślnym wysłaniu powiadomienia
    return True
    
from django.shortcuts import render
from django.contrib.gis.geos import Point
from reservations.models import NotificationPreference
from accounts.models import User
def radius_units_view(request):
    # Tworzymy punkt dla lokalizacji użytkownika
    user_point = Point(0, 0)
    user = User.objects.first()
    # Tworzymy przykładową preferencję powiadomień
    notification_preference = NotificationPreference.objects.create(
        user=user,
        latitude=0, 
        longitude=0, 
        radius=10  # Promień w kilometrach
    )
    
    # Sprawdzamy odległość dla różnych wartości
    distances_to_test = [5000, 150000]  # Odległości w metrach
    
    results = []
    
    for distance in distances_to_test:
        # Sprawdzamy, czy odległość mieści się w zasięgu promienia
        if distance <= notification_preference.radius * 1000:  # Zamiana kilometrów na metry
            result = f"Odległość {distance} metrów: MIEŚCI SIĘ w promieniu {notification_preference.radius} kilometrów"
        else:
            result = f"Odległość {distance} metrów: NIE MIEŚCI SIĘ w promieniu {notification_preference.radius} kilometrów"
        results.append(result)
    
    return render(request, 'reservations/radius_units.html', {'results': results})

