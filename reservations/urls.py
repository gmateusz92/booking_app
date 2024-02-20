from django.urls import path
from. views import home, booking_list, ApartmentDetailView,  AddApartmentView, EditApartmentView, DeleteApartmentView, apartment_list , map, CalendarView, BookingView , DeleteBookingView , message_view, message_list,  booking_history , read_opinions#BookingHistoryView # inbox ,# apartment_detail, # #search  my_apartment_detail # MyApartmentView, my_apartment_detail #MyApartmentDetailView

from . import views
app_name = 'reservations'

urlpatterns = [
    path('', home, name='home'),
    

    path('apartment/<int:pk>/', ApartmentDetailView.as_view(), name='ApartmentDetailView'),
    # path('apartment/<int:pk>/', apartment_detail, name='apartment_detail'),
    path('booking_list', booking_list, name='booking_list'),
    path('add_apartment', AddApartmentView.as_view(), name='AddApartmentView'),
    path('edit_apartment/<int:pk>', EditApartmentView.as_view(), name='EditApartmentView'),
    path('delete_apartment/<int:pk>', DeleteApartmentView.as_view(), name='DeleteApartmentView'),
    # path('my_apartment/<int:pk>/', MyApartmentView.as_view(), name='MyApartmentView'),
    # # path('apartment/<int:apartment_id>/', MyApartmentDetailView.as_view(), name='MyApartmentDetailView'),
    # path('my_apartment_detail/<int:pk>/', my_apartment_detail, name='my_apartment_detail'),
    path('apartment_list/', apartment_list, name='apartment_list'),
    # path('search/', search, name='search'),
    path('map', map, name="map"),
    # path('apartment/<int:pk>/calendar', CalendarView.as_view(), name='calendar'),
    path('calendar', CalendarView.as_view(), name='calendar'),
    path('apartment/<int:pk>/reserve/', BookingView.as_view(), name='BookingView'),
    path('delete_booking/<int:pk>', DeleteBookingView.as_view(), name='DeleteBookingView'),
   
    path('message/<int:booking_id>/', message_view, name='message_view'),
    path('messages/', message_list, name='message_list'),
   
     path('apartment/<int:apartment_id>/opinions/', read_opinions, name='read_opinions'),
    # path('apartment/<int:apartment_id>/opinions/', view_opinions, name='view_opinions'),
    path('booking_history/', booking_history, name='booking_history'),
   # path('booking_history/<int:apartment_id>/<int:booking_id>/', BookingHistoryView.as_view(), name='booking_history'),
    

]

    # path('new_reservation_email/', new_reservation_email, name='new_reservation_email'),
    
    
    
    
