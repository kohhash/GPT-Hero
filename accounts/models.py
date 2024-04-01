from django.db import models
from django.contrib.auth.models import User

class UserExtraFields(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE , related_name='extra')
    openai_api_key=models.CharField(null=True, max_length=200 , blank=True)
    prowritingaid_api_key=models.CharField(null=True, max_length=200 , blank=True)
    hide_api_key = models.BooleanField(default=False)
    salt=models.CharField(max_length=200 , blank=True , null=True)
    subscribed=models.BooleanField(default=False )
    subscription_id=models.CharField(null=True, max_length=200 , blank=True )
    usage=models.IntegerField(blank=True , default=0)

    def __str__(self):
        return self.user.username
    



    