from django.urls import path
from. views import registerUser, index, login, logout,  custDashboard, vendorDashboard

from . import views
app_name = 'accounts'

urlpatterns = [
    
    path('index/', index, name='index'),
    path('registerUser/', registerUser, name='registerUser'),
    # path('registerVendor/', registerVendor, name='registerVendor'),

    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    # path('myAccount/', myAccount, name='myAccount'), #customer albo vender
    path('custDashboard/', custDashboard, name='custDashboard'),
    path('vendorDashboard/', vendorDashboard, name='vendorDashboard'),
]