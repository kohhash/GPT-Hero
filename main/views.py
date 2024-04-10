from django.shortcuts import render, redirect
from app.essay_rephraser import process_essay
from app.load_resources import ResourceValues
from app.ai_detector import copyleaks_detector, gptzero_detector
from accounts.models import UserExtraFields
from django.contrib.auth.models import User
from django.http import HttpResponse

from .models import Essays , Plans , SubScription 
from .models import SettingsModel
from .forms import SettingsModelForm    
from .stripe_handler import stripe_purchase_url, stripe_special_purchase_url, cancel_subscription
from .forms import SetKeyForm
from django.contrib import messages
import stripe
from configurations.configuration import Configuration

# imoprt login view from django-allauth
from allauth.account.views import LoginView, SignupView, LogoutView

import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Access environment variables
OPEN_API_KEY = os.getenv('OPEN_API_KEY')
PWAID_KEY = os.getenv('PWAID_KEY')


stripe.api_key=ResourceValues.stripe_key

def rephase_essay_view(request, id):
    essay = Essays.objects.get(id=id)
    ai_detection_result = {
        True: ResourceValues.ai_detection,
        False: ResourceValues.human_detection,
    }
    gptzero_res = ai_detection_result[gptzero_detector(essay.rephrased_essay)]
    copyleaks_res = ai_detection_result[copyleaks_detector(essay.rephrased_essay)]
    return render(request, "main/rephrase.html", {"essay": essay , 'gptzero_res': gptzero_res, 'copyleaks_res': copyleaks_res})

def cancel_sub(request, id):
    cancel_subscription(id)
    return redirect('profile')

def logout_redirect_view(request):
    return redirect('account_logout')

def profile_view(request):
    user=User.objects.get(username=request.user)
    user_fields=UserExtraFields.objects.get(user=request.user)
    print("User Fields" , user)
    if request.GET.get('id'):
        stripe_id = request.GET.get('id')
        session = stripe.checkout.Session.retrieve(stripe_id)
        metadata = session.get("metadata", {})
        if metadata:
            subscription_id=session.get('subscription')
            setattr(user_fields, 'subscribed', True)
            user_fields.save()
            setattr(user_fields, 'subscription_id', subscription_id)
            user_fields.save()
            # Set default API keys for subscribed users
            setattr(user_fields, 'prowritingaid_api_key', ResourceValues.openai_api_key_default_val)
            user_fields.save()
            setattr(user_fields, 'openai_api_key', ResourceValues.prowritingaid_api_key_default_val)
            user_fields.save()
        
    if not user.is_staff:
        stripe_url=stripe_purchase_url(user)
    else:
        stripe_url=stripe_special_purchase_url(user)

    # User rephrased essay info
    essays=Essays.objects.filter(user=user)
    if len(essays)==0:
        essays=None
    form = SetKeyForm()
    print(request.method)
    settings_form = SettingsModelForm()
    try:
        settings = SettingsModel.objects.get(user=user)
        initial_data = {
            'approach': settings.approach,
            'model': settings.model,
            'context': settings.context,
            'randomness': settings.randomness,
            'tone': settings.tone,
            'difficulty': settings.difficulty,
            'adj': settings.adj,
        }
        print(initial_data)
        settings_form = SettingsModelForm(instance=settings)
    except SettingsModel.DoesNotExist:
        settings_form = SettingsModelForm()
    
    if request.method == "POST":
        if 'settings-form-submit' in request.POST:            
            approach = request.POST.get('approach')
            model = request.POST.get('model')
            context = request.POST.get('context', False)
            if context == "context":
                context = True
            else: context = False            
            randomness = int(request.POST.get('randomness'))
            tone = request.POST.get('tone')
            difficulty = request.POST.get('difficulty')
            adj = request.POST.get('adj')
            print(randomness)
            # Retrieve the existing settings for the user
            try:
                print("creating settings storage")
                settings, _ = SettingsModel.objects.get_or_create(user=user)
                print("set settings attributes")
                # Update the settings with the new form data
                settings.approach = approach
                settings.model = model
                settings.context = context
                settings.randomness = randomness
                settings.tone = tone
                settings.difficulty = difficulty
                settings.adj = adj

                print(settings)

                # Save the updated settings to the database
                settings.save()

                return redirect('profile')
            except Exception as e:
                print(e)
        else:
            data=request.POST
            if data['openai_api_key']:
                setattr(user_fields, 'openai_api_key', data['openai_api_key'])
                user_fields.save()
    # Render the template with the settings form and other data
    return render(request, "main/profile.html", {
        "settings_form": settings_form,
        "user": user,
        "user_fields": user_fields,
        "stripe_url": stripe_url,
        "essays": essays
    })


def landing_view(request):

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        return redirect("accounts/login")
    return render(request, "main/index.html")

# Create your views here.
def home_view(request):
    print("Home View" , request.user)
    if not request.user.is_authenticated:
        return redirect("account_login")

    reph_essay=None
    orig_essay=None
    is_user_provided_key = False
    openai_api_key = UserExtraFields.objects.get(user=request.user).openai_api_key

    prowritingaid_api_key=UserExtraFields.objects.get(user=request.user).prowritingaid_api_key
    hide_api_key = UserExtraFields.objects.get(user=request.user).hide_api_key

    if prowritingaid_api_key == "" or prowritingaid_api_key == None:
        prowritingaid_api_key = Configuration.DefaultValues.PROWRITINGAID_API_KEY

    if request.method == "GET":
        return render(request, "main/home.html", {"request":request, "result":reph_essay, "orig":orig_essay, "openai_api_key":openai_api_key, "prowritingaid_api_key":prowritingaid_api_key , "hide_key":hide_api_key})

    user=User.objects.get(username=request.user)
    settings = SettingsModel.objects.get(user=user)
    
    essay=request.POST.get('textarea')
    approach=settings.approach
    context=settings.context
    if context==None:
        context=False
    else:
        context=True
    randomness=settings.randomness
    tone=settings.tone
    difficulty=settings.difficulty
    additional_adjectives=settings.adj
    model=settings.model
    if request.user.subscription.is_active==False:
        openai_api_key=UserExtraFields.objects.get(user=request.user).openai_api_key
        if openai_api_key == "" or openai_api_key == None or str(openai_api_key).strip() == "":
            messages.warning(request, "Please set your OpenAI API key in profile page. ")
            return redirect("profile")
        is_user_provided_key = True
    else:
        check_sub = check_user_subscription(request.user)
        print("check_sub" , check_sub)
        if check_sub == False:
            messages.warning(request, "Your subscription has expired or usage is exceed! Please upgrade or renew your plan or add your own api key on profile.")
            return redirect("plans")
        openai_api_key=Configuration.DefaultValues.OPEN_API_KEY
    
    try:
        rephrase_essay = process_essay(
            essay=essay,
            approach=approach,
            context=context,
            randomness=randomness,
            tone=tone,
            difficulty=difficulty,
            additional_adjectives=additional_adjectives,
            openaiapikey=openai_api_key,
            pwaidapikey=prowritingaid_api_key,
            # openaiapikey=OPEN_API_KEY,
            # pwaidapikey=PWAID_KEY,
            username=request.user.username,
            model=model,
        )
        essay = Essays.objects.create(
            original_essay=essay,
            rephrased_essay=rephrase_essay,
            user=request.user,
        )
        essay.save()
        reph_essay=essay.rephrased_essay
        orig_essay=essay.original_essay
        if not is_user_provided_key:
            print("User provided key")
            user_subscription = SubScription.objects.get(user=request.user)
            user_subscription.usage += len(orig_essay.split())
            user_subscription.save()

        # ai_detection_result = {
        #     True: ResourceValues.ai_detection,
        #     False: ResourceValues.human_detection,
        # }
        # gptzero_res = ai_detection_result[gptzero_detector(rephrase_essay)]
        # copyleaks_res = ai_detection_result[copyleaks_detector(rephrase_essay)]
        messages.success(request, "Essay rephrased successfully!")
        # return redirect("rephrase", id=essay.id)
    except Exception as e:
        reph_essay=None
        orig_essay=None
        messages.warning(request, "Error occured while rephrasing essay!")
    return render(request, "main/home.html", {"request":request, "result":reph_essay, "orig":orig_essay, "openai_api_key":openai_api_key, "prowritingaid_api_key":prowritingaid_api_key , "hide_key":hide_api_key})


from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import stripe
import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import time


def plans_page_view(request):
    plans = Plans.objects.all()
    return render(request, "main/plans.html" , {'plans': plans})

def history_page_view(request):
    user = request.user
    essays_list = Essays.objects.filter(user=user).order_by('-timefield')
    paginator = Paginator(essays_list, 10)  
    page = request.GET.get('page')
    try:
        essays = paginator.page(page)
    except PageNotAnInteger:
        essays = paginator.page(1)
    except EmptyPage:
        essays = paginator.page(paginator.num_pages)
    if len(essays_list) == 0:
        essays = None

    return render(request, "main/history.html", {'essays': essays})

def payment_post(request, pk):
    print("payment_post")
    if not request.user.is_authenticated:
        return redirect("account_login")
    stripe.api_key = Configuration.STRIPE_API.PRIVATE_KEY
    def find_product_id_by_name(product_name):
        # List all products and find the matching product ID(s)
        response = stripe.Product.list(limit=100)  # You can paginate through products if necessary
        for product in response.auto_paging_iter():
            if product['name'] == product_name:
                yield product['id']

    def find_price_ids_by_product_id(product_id):
        # List all prices for the given product ID
        response = stripe.Price.list(limit=100)  # You can paginate through prices if necessary
        for price in response.auto_paging_iter():
            if price['product'] == product_id:
                yield price['id']
    price_id = ""
    for product_id in find_product_id_by_name(pk):    
        for _price_id in find_price_ids_by_product_id(product_id):
            price_id = _price_id

    print(stripe.api_key)
    user = request.user    
    print(request.method)
    if request.method == 'POST':
        print(user.id)
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {                        
                        # 'price': 'price_1NBbrkImNVsu0KeiEPOf3Gnu',
                        'price': price_id,
                        'quantity': 1
                    },
                ],
                mode='subscription',
                success_url=Configuration.STRIPE_API.REDIRECT_URI + '/payment_successful?session_id={CHECKOUT_SESSION_ID}&user_id=' + str(user.id),
                cancel_url=Configuration.STRIPE_API.REDIRECT_URI + '/payment_cancelled',
            )
            return redirect(checkout_session.url, code=303)
        except Exception as E:
            print("error: ", E)
    plans = Plans.objects.all()
    return render(request, "main/plans.html" , {'plans': plans})


## use Stripe dummy card: 4242 4242 4242 4242
@csrf_exempt
def payment_successful(request):
    stripe.api_key = Configuration.STRIPE_API.PRIVATE_KEY
    checkout_session_id = request.GET.get('session_id', None)
    session = stripe.checkout.Session.retrieve(checkout_session_id)
    customer = stripe.Customer.retrieve(session.customer)
    print("Customer " , customer)
    print("Session" , session)

    user_id = request.GET.get('user_id', None)
    user_subscription = SubScription.objects.get(user=user_id)
    print("User Subscription" , user_subscription)
    user_subscription.stripe_id = checkout_session_id
    user_subscription.customer_id = customer.id
    user_subscription.save()

    return render(request, 'main/payment_successful.html', {'customer': customer})

@csrf_exempt
def payment_cancelled(request):
    stripe.api_key = Configuration.STRIPE_API.PRIVATE_KEY
    return render(request, 'main/payment_cancelled.html')


@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = Configuration.STRIPE_API.PRIVATE_KEY
    payload = request.body
    time.sleep(10)
    print("Signature" , request.META['HTTP_STRIPE_SIGNATURE'])
    signature_header = request.META['HTTP_STRIPE_SIGNATURE']
    print("Header" , request.headers['STRIPE_SIGNATURE'])
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload, signature_header, Configuration.STRIPE_API.STRIPE_WEBHOOK_SECRET
        )
        print("Event" , event)
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        print("Session Webhook Completed" , session)
        session_id = session.get('id', None)
        subscription = SubScription.objects.get(stripe_id=session_id)
        subscription.is_active = True
        subscription.last_payment_date = datetime.datetime.now()
        subscription.usage = 0
        subscription.save()
    
    if event['type'] == 'customer.subscription.deleted':
        session = event['data']['object']
        print("Session Webhook Deleted" , session)
        session_id = session.get('customer', None)
        subscription = SubScription.objects.get(customer_id=session_id)
        subscription.is_active = False
        subscription.usage = 0
        subscription.plan = None
        subscription.stripe_id = None
        subscription.save()

    return HttpResponse(status=200)



## check if user is subscribed or not and has permission to rephrase
def check_user_subscription(user):
    user_subscription = SubScription.objects.get(user=user)
    user_usage = user_subscription.usage
    user_plan = user_subscription.plan.words_length
    if user_usage >= user_plan:
        return False
    return True
