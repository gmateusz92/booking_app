from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from accounts.models import User, UserProfile

    # ta funkcja służy do automatycznego tworzenia user profile przy tworzeniu konta uzytkownika
@receiver(post_save, sender=User)
def post_save_create_profile_receiver(sender, instance, created, **kwargs):    
    if created:
        UserProfile.objects.create(user=instance)
        print('user profile is created')
    else:
        try:
            profile = UserProfile.objects.get(user=instance) #jezelu update profilu
            profile.save()
        except:
            #create the userprofile if not exist
            UserProfile.objects.create(user=instance)
            print('profile was not exist but i created one')
        print('user is updated')

# @receiver(pre_save, sender=User)
# def pre_save_profile_receiver(sender, instance, **kwargs):
#     print(instance.username, 'this user is')
# # post_save.connect(post_save_create_profile_receiver, sender=User) 