from django.contrib import admin

# Register your models here.

from .models import Essays, User

admin.site.register(Essays)
admin.site.register(User)