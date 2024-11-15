from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Avg, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic import ListView

from accounts.models import UserProfile
from accounts.utils import send_verification_email

from .forms import (ApartmentForm, BookingForm, CommentForm,
                    NotificationPreferenceForm, PhotoForm)
from .models import *
from .models import Apartment, Booking, Message, NotificationPreference, Photo
from .utils import Calendar, check_location, get_date, get_weather_data


def home(request):
    query = request.GET.get("q", "")
    auto_complete_query = request.GET.get("id_address", "")
    query = auto_complete_query if auto_complete_query else query
    sort_by_price = request.GET.get("sort_by_price")
    apartments = Apartment.objects.all()

    for apartment in apartments:
        average_rating = Booking.objects.filter(name=apartment).aggregate(
            Avg("rating")
        )["rating__avg"]
        if average_rating is not None:
            apartment.average_rating = round(average_rating, 2)
        else:
            apartment.average_rating = "No Ratings"

    if query:
        keywords = query.split(", ")
        if len(keywords) >= 1:
            apartments = Apartment.objects.filter(
                Q(country__icontains=query)
                | Q(city__icontains=query)
                | Q(country__icontains=keywords[0])
                | Q(city__icontains=keywords[0])
            )
            if len(keywords) >= 2:
                apartments = apartments.filter(
                    Q(country__icontains=keywords[1]) & Q(city__icontains=keywords[0])
                )
    if sort_by_price == "asc":
        apartments = apartments.order_by("price")
    elif sort_by_price == "desc":
        apartments = apartments.order_by("-price")

    weather_data = get_weather_data(query)

    context = {
        "apartments": apartments,
        "weather_data": weather_data,
    }
    return render(request, "home.html", context)


class ApartmentDetailView(View):
    template_name = "reservations/apartment_detail.html"

    def get(self, request, pk):
        apartment = get_object_or_404(Apartment, pk=pk)
        photo = Photo.objects.all()
        apartments = Apartment.objects.all()
        # d = get_date(request.GET.get('day', None))
        # year, month = d.year, d.month
        # prev_month = date(year, month, 1) - timedelta(days=1)
        # prev_month_url = reverse('reservations:calendar') + f'?day={prev_month.year}-{prev_month.month}'
        # next_month = date(year, month, 28) + timedelta(days=7)
        # next_month_url = reverse('reservations:calendar') + f'?day={next_month.year}-{next_month.month}'

        # cal = Calendar(year, month, apartment)
        # html_cal = cal.formatmonth(withyear=True)

        context = {
            "apartment": apartment,
            "photo": photo,
            "apartments": apartments,
            # 'calendar': mark_safe(html_cal),
            # 'prev_month_url': prev_month_url,
            # 'next_month_url': next_month_url,
        }

        return render(request, "reservations/apartment_detail.html", context)


@login_required
def apartment_list(request):
    user = request.user
    apartments = Apartment.objects.filter(user=user)
    return render(
        request, "reservations/apartment_list.html", {"apartments": apartments}
    )


class AddApartmentView(View):
    template_name = "reservations/add_apartment.html"

    def get(self, request):
        form = ApartmentForm()
        photo_form = PhotoForm()
        return render(
            request, self.template_name, {"form": form, "photo_form": photo_form}
        )

    def post(self, request):
        form = ApartmentForm(request.POST)
        photo_form = PhotoForm(request.POST, request.FILES)
        if form.is_valid() and photo_form.is_valid():
            apartment = form.save(commit=False)
            apartment.user = request.user
            apartment.save()
            for image in request.FILES.getlist("image"):
                photo = Photo(apartment=apartment, image=image)
                photo.save()
            check_location(apartment.pk)
            return redirect("reservations:ApartmentDetailView", pk=apartment.pk)

        return render(
            request, self.template_name, {"form": form, "photo_form": photo_form}
        )


class EditApartmentView(View):
    template_name = "reservations/edit_apartment.html"

    def get(self, request, pk):
        apartment = get_object_or_404(Apartment, pk=pk, user=request.user)
        form = ApartmentForm(instance=apartment)
        photo_form = PhotoForm(instance=apartment.photos.first())
        return render(
            request,
            self.template_name,
            {"form": form, "apartment": apartment, "photo_form": photo_form},
        )

    def post(self, request, pk):
        apartment = get_object_or_404(Apartment, pk=pk, user=request.user)
        form = ApartmentForm(request.POST, instance=apartment)
        photo_form = PhotoForm(request.POST, request.FILES)
        if form.is_valid() and photo_form.is_valid():
            apartment = form.save(commit=False)
            apartment.user = request.user
            apartment.save()
            # Usuwanie zaznaczonych zdjęć
            delete_photos_ids = request.POST.getlist("delete_photos")
            for photo_id in delete_photos_ids:
                photo = Photo.objects.get(pk=photo_id)
                photo.delete()
            # Dodawanie nowych zdjęć
            for image in request.FILES.getlist("image"):
                photo = Photo(apartment=apartment, image=image)
                photo.save()
            return redirect("reservations:ApartmentDetailView", pk=apartment.pk)
        return render(
            request,
            self.template_name,
            {"form": form, "apartment": apartment, "photo_form": photo_form},
        )


class DeleteApartmentView(View):
    template_name = "reservations/delete_apartment.html"

    def get(self, request, pk):
        apartment = get_object_or_404(Apartment, pk=pk)
        return render(request, self.template_name, {"apartment": apartment})

    def post(self, request, pk):
        apartment = get_object_or_404(Apartment, pk=pk)
        apartment.delete()
        if Apartment.objects.filter(user=request.user).exists():
            return redirect("reservations:apartment_list")
        else:
            return redirect("reservations:home")


@login_required
def booking_list(request):
    user = request.user
    current_date = date.today()
    bookings = Booking.objects.filter(user=user, check_in__gte=current_date)
    context = {"bookings": bookings}
    return render(request, "reservations/bookinglist.html", context)


@login_required
def vendor_booking_list(request):
    user = request.user
    current_date = date.today()
    user_apartments = Apartment.objects.filter(user=user)
    owner_bookings = []
    for apartment in user_apartments:
        bookings = Booking.objects.filter(name=apartment, check_in__gte=current_date)
        owner_bookings.extend(bookings)
    context = {"bookings": owner_bookings}
    return render(request, "reservations/vendor_booking_list.html", context)


# class CalendarView(ListView):
#     model = Booking
#     template_name = 'reservations/calendar.html'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         d = get_date(self.request.GET.get('day', None))
#         year, month = d.year, d.month
#         prev_month = date(year, month, 1) - timedelta(days=1)
#         prev_month_url = reverse('reservations:calendar') + f'?day={prev_month.year}-{prev_month.month}'
#         next_month = date(year, month, 28) + timedelta(days=7)
#         next_month_url = reverse('reservations:calendar') + f'?day={next_month.year}-{next_month.month}'
#         cal = Calendar(year, month)
#         html_cal = cal.formatmonth(withyear=True)
#         context['calendar'] = mark_safe(html_cal)
#         context['prev_month_url'] = prev_month_url
#         context['next_month_url'] = next_month_url

#         return context


class BookingView(View):
    template_name = "reservations/reserve_apartment.html"

    def get(self, request, pk):
        apartment = get_object_or_404(Apartment, pk=pk)
        d = get_date(request.GET.get("day", None))
        year, month = d.year, d.month
        prev_month = date(year, month, 1) - timedelta(days=1)
        prev_month_url = (
            reverse("reservations:BookingView", kwargs={"pk": pk})
            + f"?day={prev_month.year}-{prev_month.month}"
        )
        next_month = date(year, month, 28) + timedelta(days=7)
        next_month_url = (
            reverse("reservations:BookingView", kwargs={"pk": pk})
            + f"?day={next_month.year}-{next_month.month}"
        )
        cal = Calendar(year, month, apartment)
        html_cal = cal.formatmonth(withyear=True)
        form = BookingForm(initial={"name": apartment.id})

        context = {
            "apartment": apartment,
            "calendar": mark_safe(html_cal),
            "prev_month_url": prev_month_url,
            "next_month_url": next_month_url,
            "form": form,
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        apartment = get_object_or_404(Apartment, pk=pk)
        form = BookingForm(request.POST)
        if form.is_valid():
            check_in = form.cleaned_data["check_in"]
            check_out = form.cleaned_data["check_out"]
            # Sprawdzenie, czy nowa rezerwacja nakłada się na istniejące
            overlapping_bookings = Booking.objects.filter(
                Q(
                    check_out__gt=check_in, check_in__lt=check_out
                )  # zarezerwowany przed wyjazdem lub po zameldowaniu
                | Q(
                    check_in__lt=check_out, check_out__gt=check_in
                ),  # wyjazd zameldowano przed zameldowaniem lub po zameldowaniu
                name=apartment,  # pole identyfikujące apartament w modelu Booking
            )
            if overlapping_bookings.exists():
                messages.error(
                    request,
                    _("This apartment is already booked for the selected dates."),
                )
            elif (
                Booking.objects.filter(check_in=check_out).exists()
                or Booking.objects.filter(check_out=check_in).exists()
            ):
                messages.error(
                    request,
                    _("This apartment is already booked for the selected dates."),
                )
            else:
                # Tworzenie nowej rezerwacji
                booking = form.save(commit=False)
                booking.user = request.user
                booking.name = apartment  # przypisanie apartamentu do rezerwacji
                booking.save()

                user = apartment.user
                mail_subject = _("You have a new reservation!")
                email_template = "emails/reservation_done.html"
                send_verification_email(request, user, mail_subject, email_template)
                return redirect("reservations:booking_list")

        d = get_date(request.GET.get("day", None))
        year, month = d.year, d.month
        prev_month = date(year, month, 1) - timedelta(days=1)
        prev_month_url = (
            reverse("reservations:BookingView", kwargs={"pk": pk})
            + f"?day={prev_month.year}-{prev_month.month}"
        )
        next_month = date(year, month, 28) + timedelta(days=7)
        next_month_url = (
            reverse("reservations:BookingView", kwargs={"pk": pk})
            + f"?day={next_month.year}-{next_month.month}"
        )
        cal = Calendar(year, month, apartment)
        html_cal = cal.formatmonth(withyear=True)

        context = {
            "apartment": apartment,
            "calendar": mark_safe(html_cal),
            "prev_month_url": prev_month_url,
            "next_month_url": next_month_url,
            "form": form,
        }
        return render(request, self.template_name, context)


class DeleteBookingView(View):
    template_name = "reservations/delete_booking.html"

    def get(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk)
        return render(request, self.template_name, {"booking": booking})

    def post(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk)
        booking.delete()
        if Booking.objects.filter(user=request.user).exists():
            return redirect("reservations:booking_list")
        else:
            return redirect("reservations:home")


@login_required
def message_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    apartment = booking.name
    if request.method == "POST":
        content = request.POST.get("content")
        sender = request.user
        receiver = booking.user
        message = Message.objects.create(
            sender=sender, receiver=receiver, booking=booking, content=content
        )
        if sender == apartment.user:
            subject = "You have a new message."
            template = "emails/new_message.html"
            context = {"message": message}
            html_message = render_to_string(template, context)
            send_mail(subject, "", None, [receiver.email], html_message=html_message)
        else:
            subject = "You have a new message."
            template = "emails/new_message.html"
            context = {"message": message}
            html_message = render_to_string(template, context)
            send_mail(
                subject, "", None, [apartment.user.email], html_message=html_message
            )

    messages = Message.objects.filter(booking=booking)
    for message in messages:
        message.sender_profile = UserProfile.objects.get(user=message.sender)
    return render(
        request,
        "reservations/message.html",
        {"booking": booking, "apartment": apartment, "messages": messages},
    )


def read_opinions(request, apartment_id):
    bookings = Booking.objects.filter(name_id=apartment_id).exclude(comment=None)
    return render(request, "reservations/view_opinion.html", {"bookings": bookings})


@login_required
def booking_history(request):
    current_datetime = date.today()
    bookings = Booking.objects.filter(user=request.user, check_out__lt=current_datetime)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            booking_id = form.cleaned_data["booking_id"]
            comment_content = form.cleaned_data["comment"]
            rating_value = form.cleaned_data["rating"]
            booking = Booking.objects.get(id=booking_id)
            booking.comment = comment_content
            booking.rating = rating_value
            booking.save()
    else:
        form = CommentForm()
    return render(
        request,
        "reservations/booking_history.html",
        {"bookings": bookings, "form": form},
    )


class AddNotificationPreferenceView(View):
    template_name = "reservations/notification_preference.html"

    def get(self, request):
        preferences = NotificationPreference.objects.filter(user=request.user)
        form = NotificationPreferenceForm()
        return render(
            request, self.template_name, {"form": form, "preferences": preferences}
        )

    def post(self, request):
        form = NotificationPreferenceForm(request.POST)
        if form.is_valid():
            notification = form.save(commit=False)
            notification.user = request.user
            notification.save()
            return redirect("reservations:AddNotificationPreferenceView")
        return render(request, self.template_name, {"form": form})


class DeletePreferenceView(View):
    def get(self, request, pk):
        preference = NotificationPreference.objects.get(pk=pk)
        if preference.user == request.user:
            preference.delete()
        return redirect("reservations:AddNotificationPreferenceView")
