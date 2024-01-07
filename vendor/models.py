from django.db import models

# Create your models here.
from django.db import models
from accounts.models import User, UserProfile
from accounts.utils import send_notification
from datetime import time, date, datetime


class Vendor(models.Model):
    user = models.OneToOneField(User, related_name='user', on_delete=models.CASCADE)
    user_profile = models.OneToOneField(UserProfile, related_name='userprofile', on_delete=models.CASCADE)
    vendor_name = models.CharField(max_length=50)
    vendor_slug = models.SlugField(max_length=100, unique=True)
    vendor_license = models.ImageField(upload_to='vendor/license')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.vendor_name
    
    def is_open(self):
        today_date = date.today()
        today = today_date.isoweekday() #zwraca ktory to dzien tygodnia np poniedzialek to 1 itd 

        current_opening_hours = OpeningHour.objects.filter(vendor=self, day=today)
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S") #konwertuje na string
    
        is_open = None
        for i in current_opening_hours:
            if not i.is_closed:
                start = str(datetime.strptime(i.from_hour, "%I:%M %p").time()) #time daje tylko time
                end = str(datetime.strptime(i.to_hour, "%I:%M %p").time()) 
                print(start, end)
                if current_time > start and current_time < end:
                    is_open = True
                    break #bo bedzie robic w kolko
            else:
                is_open = False    
        return is_open    
    
    # ackeptacja przez admina restauracji lub konta i wyslanie powiadomienia
    def save(self, *args, **kwargs): #uzywamy gdy nie wiemy ile parametrow bedzie miala funkcja
        if self.pk is not None: #oznacza update tego szczegolnego obiektu
            orig = Vendor.objects.get(pk=self.pk) #oznacza ze self topic zostal juz stworzony, orig= oryginalne zaznaczenie is approved
            if orig.is_approved != self.is_approved:
                mail_template = 'accounts/emails/admin_approval_email.html'
                context = {
                           'user': self.user,
                           'is_approved': self.is_approved,
                           'to_email': self.user.email,
                    }
                if self.is_approved == True:
                    #send notification email
                    mail_subject = "Congratulations! Your restaurant has been approved"
                    send_notification(mail_subject, mail_template, context)
                else:
                    #send notification email
                    mail_subject = "We are sorry, you are not eligible for publishing your food menu on our marketplace"
                    send_notification(mail_subject, mail_template, context)    

        return super(Vendor, self).save(*args, **kwargs) #super umozliwia dostep do save method tej szczegolnej klasy(vendor)
    
DAYS = [
    (1, ("Monday")),
    (2, ("Tuesday")),
    (3, ("Wednesday")),
    (4, ("Thursday")),
    (5, ("Friday")),
    (6, ("Saturday")),
    (7, ("Sunday")),
]

HOUR_OF_DAY_24 = [(time(h, m).strftime('%I:%M %p'), time(h, m).strftime('%I:%M %p')) for h in range(0, 24) for m in (0, 30)]

class OpeningHour(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    day = models.IntegerField(choices=DAYS)
    from_hour = models.CharField(choices=HOUR_OF_DAY_24, max_length=10, blank=True)
    to_hour = models.CharField(choices=HOUR_OF_DAY_24, max_length=10, blank=True)
    is_closed = models.BooleanField(default=False)

    class Meta:
        ordering = ('day', '-from_hour') #porzadkuje wg godzin otwarcia
        unique_together = ('vendor', 'day', 'from_hour', 'to_hour')

    def __str__(self): 
        return self.get_day_display() # day bo day mamy w models
