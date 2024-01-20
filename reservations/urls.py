from django.urls import path
from. views import home, booking_list, apartment_detail, AddApartmentView, EditApartmentView, DeleteApartmentView

from . import views
app_name = 'reservations'

urlpatterns = [
    path('', home, name='home'),
    path('apartment/<int:pk>/', apartment_detail, name='apartment_detail'),
    path('booking_list', booking_list, name='booking_list'),
    path('add_apartment', AddApartmentView.as_view(), name='AddApartmentView'),
    path('edit_apartment/<int:pk>', EditApartmentView.as_view(), name='EditApartmentView'),
    path('delete_apartment', DeleteApartmentView.as_view(), name='DeleteApartmentView'),
    
    
]