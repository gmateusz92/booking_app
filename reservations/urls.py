from django.urls import path
from. views import home, booking_list, apartment_detail, AddApartmentView, EditApartmentView, DeleteApartmentView, apartment_list #search  my_apartment_detail # MyApartmentView, my_apartment_detail #MyApartmentDetailView

from . import views
app_name = 'reservations'

urlpatterns = [
    path('', home, name='home'),
    
    path('apartment/<int:pk>/', apartment_detail, name='apartment_detail'),
    path('booking_list', booking_list, name='booking_list'),
    path('add_apartment', AddApartmentView.as_view(), name='AddApartmentView'),
    path('edit_apartment/<int:pk>', EditApartmentView.as_view(), name='EditApartmentView'),
    path('delete_apartment/<int:pk>', DeleteApartmentView.as_view(), name='DeleteApartmentView'),
    # path('my_apartment/<int:pk>/', MyApartmentView.as_view(), name='MyApartmentView'),
    # # path('apartment/<int:apartment_id>/', MyApartmentDetailView.as_view(), name='MyApartmentDetailView'),
    # path('my_apartment_detail/<int:pk>/', my_apartment_detail, name='my_apartment_detail'),
    path('apartment_list/', apartment_list, name='apartment_list'),
    # path('search/', search, name='search'),
    
    
    
    
]