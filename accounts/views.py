from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import UserForm
from .models import User, UserProfile
from django.contrib import messages, auth
from vendor.forms import VendorForm
from accounts.utils import send_verification_email
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator

from django.core.exceptions import PermissionDenied
from django.template.defaultfilters import slugify
from vendor.models import Vendor

def index(request):
    return render(request, 'index.html')

# Restrict the vendor from accessing the custoer page
# def check_role_vendor(user):
#     if user.role == 1:
#         return True
#     else:
#         raise PermissionDenied
    
# # Restrict the customer from accessing the vendor page
# def check_role_customer(user):
#     if user.role == 2:
#         return True
#     else:
#         raise PermissionDenied #w template 403.html ktory mowi co oznacza ten bląd


def registerUser(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in!')
        return redirect('accounts:index')
    elif request.method == 'POST':
        print(request.POST)
        form = UserForm(request.POST)
        if form.is_valid():
            # 1) Create the user using form
            # password = form.cleaned_data['password'] #do ukrycia password
            # user = form.save(commit=False)# jest gotowe do zapisania ale nie zapisane
            # user.set_password(password) #do ukrycia password
            # user.role = User.CUSTOMER #przypisujemy role uzytkownika
            # user.save()
            

            # 2) Create the user using create_user method
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            # user.role = User.CUSTOMER
            user.save()

            # send verification email

            # mail_subject = 'Please activate your account'
            # email_template = 'accounts/emails/account_verification_email.html'
            # send_verification_email(request, user, mail_subject, email_template) #funkcja dynamiczna
            # messages.success(request, 'Your account has been registered sucessfully!')

            messages.error(request, 'Your acc has been register succesfully') # error to jest kolor z bootstrap ustawienia settings
            return redirect('accounts:registerUser')
        else:
            print(form.errors)   
    else:
        form = UserForm()
    context = {
        'form': form
    }

    return render(request, 'accounts/registerUser.html', context)


#rejestracja restauracji/ sprzedawcy
# def registerVendor(request):
#     if request.user.is_authenticated:
#         messages.warning(request, 'You are already logged in!')
#         return redirect('accounts:index')
#     elif request.method == 'POST':
#         # store data and create the user
#         form = UserForm(request.POST)
#         v_form = VendorForm(request.POST, request.FILES) #bo upload image
#         if form.is_valid() and v_form.is_valid():
#             first_name = form.cleaned_data['first_name'] #returns a dictionary of validated form input fields and their values, where string primary keys are returned as objects.
#             last_name = form.cleaned_data['last_name']
#             username = form.cleaned_data['username']
#             email = form.cleaned_data['email']
#             password = form.cleaned_data['password']
#             user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
#             user.role = User.VENDOR
#             user.save() #tutaj signals tworzy profil
#             vendor = v_form.save(commit=False)
#             vendor.user = user
#             vendor_name = v_form.cleaned_data['vendor_name']
#             vendor.vendor_slug = slugify(vendor_name)+'-'+str(user.id) #str nadaje unikalny nr i jak ktos poda taki sam nick to nie bedzie bledu
#             user_profile = UserProfile.objects.get(user=user)
#             vendor.user_profile = user_profile
#             vendor.save()

            # send verification email
            # mail_subject = 'Please activate your account'
            # email_template = 'accounts/emails/account_verification_email.html'
            # send_verification_email(request, user, mail_subject, email_template)

            # messages.success(request, 'Your acc has been registered successfully! Please wait for approval')
    #         return redirect('accounts:registerVendor')
    #     else:
    #         print('invalid form')
    #         print(form.errors)
    # else:
    #     form = UserForm()
    #     v_form = VendorForm()

    # context = {
    #     'form': form,
    #     'v_form': v_form,
    # }
    # return render(request, 'accounts/registerVendor.html', context)

# def activate(request, uidb64, token): #aktywacja konta
#     #Activate the user by setting the is_active status to True
#     try:
#         uid = urlsafe_base64_decode(uidb64).decode()# rozkodowuje link wyslany na email
#         user = User._default_manager.get(pk=uid)
#     except(TypeError, ValueError, OverflowError, User.DoesNotExist):
#         user = None

#     if user is not None and default_token_generator.check_token(user, token):  
#         user.is_active = True
#         user.save()
#         messages.success(request, 'Congratulation! Your account is activated')
#         return redirect('myAccount')
#     else:
#         messages.error(request, 'Invalid activation link')
#         return redirect('myAccount')

def login(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in!')
        return redirect('accounts:index')
    elif request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password) #wbudowana funkcja sprawdzajaca czy uzytkownik istnieje

        if user is not None:
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
            return redirect('accounts:index')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('accounts:login')
    return render(request, 'accounts/login.html')

def logout(request):
    auth.logout(request)
    messages.info(request, 'You are logged out.')
    return redirect('accounts:index')


# @login_required(login_url='login') #przekierowuje na strone logowania
# def myAccount(request): # w utils.py funkcja pomocnicza - przekirowuje na odpowiedni dashboard
#     user = request.user
#     redirectUrl = detectUser(user)
#     return redirect(redirectUrl)

@login_required(login_url='login')
#@user_passes_test(check_role_customer) # Restrict the vendor from accessing the customer page
def custDashboard(request):
    # orders = Order.objects.filter(user=request.user)[:5] #is_ordered=True
    # recent_orders = orders[:5]
    # context = {
    #     'orders': orders,
    #     'orders_count': orders.count(),
    #     'recent_orders': recent_orders,
    # }
    return render(request, 'accounts/custDashboard.html')


@login_required(login_url='login')
#@user_passes_test(check_role_vendor) # Restrict the vendor from accessing the customer page
def vendorDashboard(request):
    # vendor = Vendor.objects.get(user=request.user)
    # orders = Order.objects.filter(vendors__in=[vendor.id], is_ordered=True).order_by('-created_at') #dajemy vendor.id poniewaz w many to many filed django robi 3 tabele
    # recent_orders = orders[:5]
    # context = {
    #     'orders': orders,
    #     'orders_count': orders.count(),
    #     'recent_orders': recent_orders,
    # }
    
    return render(request, 'accounts/vendorDashboard.html')

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)# potrzebujemy emaila podanego przez usera

            # send reset password email - funkcja jest dynamiczna bo podaje parametry email subject i template
            email_subject = 'Reset your password'
            email_template = 'accounts/emails/reset_password_email.html'
            send_verification_email(request, user, email_subject, email_template)
            messages.success(request, 'Password reset link has been sent to your email address')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exists')
            return redirect('forgot_password')
    return render(request, 'accounts/forgot_password.html')


def reset_password_validate(request, uidb64, token):
    #validate the user by decoding the token and user pk
    try:
        uid = urlsafe_base64_decode(uidb64).decode()# rozkodowuje link wyslany na email
        user = User._default_manager.get(pk=uid) #bierzemu user z uid
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token): #jezeli token jest poprawny
        request.session['uid'] = uid
        messages.info(request, 'Please reset your password')
        return redirect('reset_password')
    else:
        messages.error(request, 'This link has been expired!')
        return redirect('myAccount')

def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password'] #'password' jest w reset_password template name="password"
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            pk = request.session.get('uid') #z wczesniej zapisanej sesji
            user = User.objects.get(pk=pk)
            user.set_password(password)
            user.is_active = True
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match')
            return redirect('reset_password')

    return render(request, 'accounts/reset_password.html')