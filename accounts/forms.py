from django import forms
from .models import User, UserProfile
from .validators import allow_only_images_validator
from django.contrib.auth.forms import AuthenticationForm

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control narrow-input'})) #poniewaz nie mamy w models
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control narrow-input'})) #poniewaz nie mamy w models
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control narrow-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control narrow-input'}),
            'username': forms.TextInput(attrs={'class': 'form-control narrow-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-control narrow-input'}),
        }

    #non field error
    def clean(self): #nadpisanie metody cleand_data zeby sprawdzic czy pass = confirm pass
        cleaned_data = super(UserForm, self).clean() #super daje mozliwosc nadpisania clean(inbuild function)
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError(
                'Password does not match'
            )

class UserProfileForm(forms.ModelForm):
    address = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Start typing...', 'required': 'required'}))
    profile_picture = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info'}), validators = [allow_only_images_validator])
   
    class Meta:
        model = UserProfile
        # fields = ['profile_picture',  'address', 'country', 'state', 'city', 'pin_code'] #'latitude', 'longitude']
        fields = [ 'profile_picture', 'address', 'country', 'state', 'city', 'pin_code']

    # bardzo przydatne
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            if field == 'latitude' or field =='longitude':
                self.fields[field].widget.attrs['readonly'] = 'readonly'


class UserInfoForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number']

        