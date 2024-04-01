
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SubScription

@receiver(post_save, sender=User)
def create_user_subscription(sender, instance, created, **kwargs):
    if created and not SubScription.objects.filter(user=instance).exists():
        SubScription.objects.create(user=instance)
