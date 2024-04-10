from django.db import models
from django.contrib.auth.models import User
from accounts.models import UserExtraFields


class Essays(models.Model):
    original_essay=models.CharField(max_length=128000)
    rephrased_essay=models.CharField(max_length=128000, null=True)
    timefield=models.DateTimeField(auto_now_add=True)
    user=models.ForeignKey(User, on_delete=models.CASCADE, null=True , related_name='essays')
    def __str__(self):
        return self.user.username + " " + str(self.timefield)

class Plans(models.Model):
    name=models.CharField(max_length=128)
    price=models.IntegerField()
    stripe_id=models.CharField(max_length=128)
    words_length = models.IntegerField()
    # api_access = models.BooleanField(default=False)
    def __str__(self):
        return self.name
    
class PlansFeatures(models.Model):
    plan=models.ForeignKey(Plans, on_delete=models.CASCADE, related_name='features')
    feature=models.CharField(max_length=128)
    def __str__(self):
        return self.plan.name + " " + self.feature
    

class SubScription(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE , related_name='subscription')
    plan=models.ForeignKey(Plans, on_delete=models.CASCADE, related_name='subscription' , null=True , blank=True)
    usage = models.IntegerField(default=0)
    last_payment_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    stripe_id=models.CharField(max_length=512 , null=True, blank=True)
    customer_id=models.CharField(max_length=512 , null=True, blank=True)
    def __str__(self):
        return self.user.username + " - " + str(self.is_active)
    
class SettingsModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    approach = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    context = models.BooleanField(default=False)
    randomness = models.IntegerField(default=1)
    tone = models.CharField(max_length=100)
    difficulty = models.CharField(max_length=100)
    adj = models.CharField(max_length=100)