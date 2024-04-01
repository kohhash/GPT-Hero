from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
from .database_handler import Database
from .form_handler import Rephrase
from .models import User, Essays
# import logging
# import traceback

# db = Database(r"C:\Users\omkar\Desktop\work\virtuaqaptive\gpt_hero\django_GPT\GPTHero\app\data\db.sqlite3")
db=Database()
rp=Rephrase(db)

def homepage(request):
    db.create_user("nami", "tangerine")
    return render(request, "app/index.html")

def login(request):
    return HttpResponse("You're looking at question login page")


def register(request):
    response = "You're looking at the register page."
    return HttpResponse(response)

def rephrase(request):
    return rp.single_essay(request)