from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from .models import UserExtraFields

@receiver(user_signed_up)
def user_signed_up_(request, user, **kwargs):
    user_extra = UserExtraFields.objects.create(user=user)
    user_extra.save()
