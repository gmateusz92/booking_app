from django.shortcuts import render, redirect
from .forms import UserForm, UserProfileForm, AuthenticationForm
from .models import User, UserProfile
from django.contrib import messages, auth
from accounts.utils import send_verification_email #send_password_reset_email
from django.contrib.auth.decorators import login_required
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import PermissionDenied
from django.template.defaultfilters import slugify
from django.contrib.auth import login, authenticate


def index(request):
    return render(request, 'index.html')


def registerUser(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in!')
        return redirect('accounts:index')
    elif request.method == 'POST':
        print(request.POST)
        form = UserForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            user.is_active = False
            user.save()

            # send verification email
            mail_subject = 'Please activate your account'
            email_template = 'emails/account_verification_email.html'
            send_verification_email(request, user, mail_subject, email_template)

            messages.error(request, 'Your acc has been register succesfully') # error to jest kolor z bootstrap ustawienia settings
            return redirect('accounts:login')
        else:
            print(form.errors)   
    else:
        form = UserForm()
    context = {
        'form': form
    }

    return render(request, 'accounts/registerUser.html', context)



def activate(request, uidb64, token): #aktywacja konta
    #Activate the user by setting the is_active status to True
    try:
        uid = urlsafe_base64_decode(uidb64).decode()# rozkodowuje link wyslany na email
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):  
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulation! Your account is activated')
        return redirect('accounts:login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('accounts:login')


# def edit_profile(request):
#     if request.method == 'POST':
#         profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
#         if profile_form.is_valid():
#             profile_form.save()
#             return redirect('profile_detail')  # Przekierowanie do widoku szczegółów profilu użytkownika
#     else:
#         profile_form = UserProfileForm(instance=request.user.profile)
#     return render(request, 'edit_profile.html', {'profile_form': profile_form})


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
            messages.error(request, 'Invalid login credentials - activate your account')
            return redirect('accounts:login')
    return render(request, 'accounts/login.html')



def logout(request):
    auth.logout(request)
    messages.info(request, 'You are logged out.')
    return redirect('accounts:index')




@login_required(login_url='login')
def myprofile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            profil = form.save(commit=False)
            profil.user = request.user
            profil.save()
            messages.success(request, 'Profil zaktualizowany pomyślnie!')
            return redirect('accounts:myprofile')  # zakładając, że masz URL o nazwie 'myprofile'
        else:
            messages.error(request, 'Błąd aktualizacji profilu. Proszę poprawić poniższe błędy.')
    else:
        form = UserProfileForm(instance=request.user.profile if hasattr(request.user, 'profile') else None)
    return render(request, 'accounts/myprofile.html', {'form': form})



def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)

            # send reset password email
            email_subject = 'Reset your password'
            email_template = 'emails/reset_password_email.html'
            send_verification_email(request, user, email_subject, email_template)
            messages.success(request, 'Password reset link has been sent to your email address')
            return redirect('accounts:login')
        else:
            messages.error(request, 'Account does not exist')
            return redirect('accounts:forgot_password')
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
        return redirect('accounts:reset_password')
    else:
        messages.error(request, 'This link has been expired!')
        return redirect('accounts:reset_password')

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
            return redirect('accounts:login')
        else:
            messages.error(request, 'Password do not match')
            return redirect('accounts:reset_password')

    return render(request, 'accounts/reset_password.html')