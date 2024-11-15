from django.urls import path
from.views import (
    home,
    booking_list,
    ApartmentDetailView,
    AddApartmentView, 
    EditApartmentView,
    DeleteApartmentView,
    apartment_list,  
    BookingView,
    DeleteBookingView,
    message_view,
    booking_history,
    AddNotificationPreferenceView,
    read_opinions,
    vendor_booking_list,
    DeletePreferenceView,  
)

app_name = 'reservations'

urlpatterns = [
    path('', home, name='home'),
    path('apartment/<int:pk>/', ApartmentDetailView.as_view(), name='ApartmentDetailView'),
    path('booking_list/', booking_list, name='booking_list'),
    path('add_apartment/', AddApartmentView.as_view(), name='AddApartmentView'),
    path('edit_apartment/<int:pk>', EditApartmentView.as_view(), name='EditApartmentView'),
    path('delete_apartment/<int:pk>', DeleteApartmentView.as_view(), name='DeleteApartmentView'),
    path('apartment_list/', apartment_list, name='apartment_list'),
    # path('calendar/', CalendarView.as_view(), name='calendar'),
    path('apartment/<int:pk>/reserve/', BookingView.as_view(), name='BookingView'),
    path('delete_booking/<int:pk>', DeleteBookingView.as_view(), name='DeleteBookingView'),
    path('message/<int:booking_id>/', message_view, name='message_view'),
    path('apartment/<int:apartment_id>/opinions/', read_opinions, name='read_opinions'),
    path('booking_history/', booking_history, name='booking_history'),
    path('vendor_booking_list/', vendor_booking_list, name='vendor_booking_list'),
    path('notification-preference/', AddNotificationPreferenceView.as_view(), name='AddNotificationPreferenceView'), 
    path('delete-preference/<int:pk>/', DeletePreferenceView.as_view(), name='DeletePreferenceView'),
    
]


    
    
    
    
