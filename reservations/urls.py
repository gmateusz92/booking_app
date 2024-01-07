from django.urls import path
from. views import home

from . import views
app_name = 'reservations'

urlpatterns = [
    path('', home, name='home'),
    
]