from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db.models.fields.related import OneToOneField
from django.contrib.gis.db import models as gismodels
from django.contrib.gis.geos import Point
from django.contrib.gis.geos import Point
from django.contrib.gis.db import models as gismodels
from django_google_maps import fields as map_fields



#baseusermanager pozwala edytowac dane przy tworzeniu uzytkownikow

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, password=None):
        if not email:
            raise ValueError('User must have an email address')

        if not username:
            raise ValueError('User must have an username')

        user = self.model(
            email = self.normalize_email(email), # jezeli wpiszesz z duzych liter zmieni na male literki
            username = username,
            first_name = first_name,
            last_name = last_name,
        )
        user.set_password(password) #set_password ustawia haslo i przechowuje w bazie danych
        user.save(using=self._db) #zapisuje w domyslnej bazie danych ustawionej w settings
        return user

    def create_superuser(self, first_name, last_name, username, email, password=None):
        user = self.create_user( #tworzymy na podstawie zwyklego(create_user) i nadamy uprawnienia
            email = self.normalize_email(email), # jezeli wpiszesz z duzych liter zmieni na male literki
            username = username,
            password = password,
            first_name = first_name,
            last_name = last_name,
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user

 

class User(AbstractBaseUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=12, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superadmin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = UserManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

     


class UserProfile(models.Model):
    user = OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='users/profile_pictures', blank=True, null=True)
    address = models.CharField(max_length=250, blank=True, null=True)
    country = models.CharField(max_length=15, blank=True, null=True)
    state = models.CharField(max_length=15, blank=True, null=True)
    city = models.CharField(max_length=15, blank=True, null=True)
    pin_code = models.CharField(max_length=6, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.user.email   


    #tworzy point w admin panel
    # def save(self, *args, **kwargs):
    #     if self.latitude and self.longitude:
    #         self.location = Point(float(self.longitude), float(self.latitude))
    #         return super(UserProfile, self).save(*args, **kwargs)
    #     return super(UserProfile, self).save(*args, **kwargs)
