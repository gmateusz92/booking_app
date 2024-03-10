from django.urls import path
from. views import registerUser, index, login, logout, my_profile, activate, forgot_password, reset_password_validate, reset_password

app_name = 'accounts'

urlpatterns = [
    
    path('index/', index, name='index'),
    path('registerUser/', registerUser, name='registerUser'),
    # path('registerVendor/', registerVendor, name='registerVendor'),

    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('myprofile/', my_profile, name='myprofile'),

    path('activate/<uidb64>/<token>', activate, name='activate'), #wysylanie linku potwierdzajacego
    path('forgot_password/', forgot_password, name='forgot_password'),
    path('reset_password_validate/<uidb64>/<token>/', reset_password_validate, name='reset_password_validate'),
    path('reset_password/', reset_password, name='reset_password'),

    # path('myAccount/', myAccount, name='myAccount'), #customer albo vender
    #ath('custDashboard/', custDashboard, name='custDashboard'),
    
]