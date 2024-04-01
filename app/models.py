from django.db import models

# Create your models here.

class User(models.Model):
    username=models.CharField(primary_key=True, max_length=100, unique=True)
    password=models.CharField(max_length=100)
    openai_api_key=models.CharField(null=True, max_length=200)
    proritingaid_api_key=models.CharField(null=True, max_length=200)
    salt=models.CharField(max_length=200)
    admin=models.BooleanField(default=False)
    special_user=models.BooleanField(default=False)
    subscribed=models.BooleanField(default=False)
    subscription_id=models.CharField(null=True, max_length=200)
    usage=models.IntegerField(null=True)


class Essays(models.Model):
    original_essay=models.CharField(max_length=64000)
    rephrased_essay=models.CharField(max_length=64000, null=True)
    timefield=models.DateTimeField(auto_now_add=True, null=True)
    byuser=models.ForeignKey(User, on_delete=models.CASCADE, null=True)
