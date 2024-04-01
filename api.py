from typing import Union

from fastapi import FastAPI


# importing moduls
import logging
import openai
from pydantic import BaseModel, validator
from fastapi import FastAPI, Body, Query, HTTPException, Header, Request
from app.load_resources import (
    ResourceValues,
    get_default_prowritingaid_key,
    get_default_openai_key,
    Approach,
    validate_password,
    validate_username,
)
from typing import Union, Annotated
from app.essay_rephraser import process_essay

# from app.user_handler import UserHandler
# from app.database_handler import Database
import json
from app.password_encrypt import password_encrypt, password_decrypt
import traceback
import stripe

# from stripe_handler import unsubscribe_subscription

# app = FastAPI()
# importing django

import os
from django.core.wsgi import get_wsgi_application
from django.db import models

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "GPTHero.settings")
application = get_wsgi_application()

from django.contrib.auth.models import User as DjangoUser
from accounts.models import UserExtraFields
from django.contrib.auth import authenticate
from typing import Dict

stripe.api_key = ResourceValues.stripe_key

approach_api_description = f"{ResourceValues.approach_tooltip if ResourceValues.approach_tooltip is not None else ''}. Options are: `{Approach.creative}` or `{Approach.conservative}`"


class APIConfig(BaseModel):
    openai_api_key: Annotated[str, Query(min_length=1)] = None
    prowritingaid_api_key: Annotated[str, Query(min_length=1)] = None


class User(BaseModel):
    username: Annotated[str, Query(min_length=4)] = None
    password: Annotated[str, Query(min_length=6)] = None
    auth_token: Annotated[str, Query(min_length=1)] = None

    class Config:
        @staticmethod
        def schema_extra(schema, model) -> None:
            schema["description"] = ResourceValues.user_description_api
            schema["summary"] = ResourceValues.user_description_api


class RephrasedEssay(BaseModel):
    rephrased_essay: str = None
    error: str = None


class Prompt(BaseModel):
    essay: Annotated[str, Query(min_length=100)]
    openaiapikey: Annotated[str, Query(min_length=3)] = None
    prowritingaidapikey: Annotated[str, Query(min_length=3)] = None
    approach: Annotated[
        str,
        Query(
            regex=f"(?i){Approach.creative.lower()}|{Approach.conservative.lower()}",
            description=approach_api_description,
        ),
    ] = ResourceValues.approach_default_val
    context: Annotated[bool, Query(description=ResourceValues.context_tooltip)] = bool(
        ResourceValues.context_default_val
    )
    randomness: Annotated[
        int, Query(description=ResourceValues.randomness_tooltip, ge=0, le=10)
    ] = int(ResourceValues.randomness_default_val)
    tone: Annotated[
        str, Query(description=ResourceValues.tone_tooltip, max_length=100)
    ] = ResourceValues.tone_default_val
    difficulty: Annotated[
        str, Query(description=ResourceValues.difficulty_tooltip, max_length=100)
    ] = ResourceValues.difficulty_default_val
    additional_adjectives: Annotated[
        str,
        Query(description=ResourceValues.additional_adjectives_tooltip, max_length=100),
    ] = ResourceValues.additional_adjectives_default_val
    model: Annotated[str, Query(description="ModelVersion", max_length=100)] = "GPT-3"

    class Config:
        @staticmethod
        def schema_extra(schema, model) -> None:
            schema["description"] = ResourceValues.prompt_description_api


app = FastAPI()
# userHandler = UserHandler()


def get_user_from_token(auth_token: str) -> (str, str):
    data = password_decrypt(auth_token, ResourceValues.token).decode("utf-8")
    data = json.loads(str(data))
    print("token data", data["username"], data["password"])
    return data["username"], data["password"]


def get_user(user: User, token_enabled=True) -> (str, str):
    username, password, token = user.username, user.password, user.auth_token

    if token and token_enabled:
        final_username, final_password = get_user_from_token(token)

    else:
        final_username, final_password = username, password

    return validate_username(final_username), validate_password(final_password)


@app.post("/rephrase_essay", description=ResourceValues.rephrase_essay_description)
def rephrase_essay(
    prompt: Prompt = Body(
        embed=True,
    ),
    user: User = Body(
        embed=True,
        default=None,
    ),
):
    prompt = prompt.dict()
    essay = prompt["essay"]
    approach = prompt["approach"]
    context = prompt["context"]
    randomness = prompt["randomness"]
    tone = prompt["tone"]
    difficulty = prompt["difficulty"]
    openai_api_key = prompt.get("openaiapikey", None)
    prowritingaid_key = prompt.get("prowritingaidapikey", None)
    additional_adjectives = prompt["additional_adjectives"]
    model = prompt["model"]
    verified_user = None
    # print(prompt , user)
    print(user)
    try:
        if user:
            username, password = get_user(user)
            print("Printing Username and password")
            
            if username and password:
                main_user = authenticate(username=username, password=password)
                print(main_user)
                if main_user is not None:
                    verified_user = main_user.username
                    print("User is Authenticated")
        print(user.username)
        # if user.username != "" and user.password != "":
        #     # username, password = get_user(user)
        #     user = authenticate(username=user.username, password=user.password)
        #     print(user)
        #     if user is not None:
        #         verified_user = user.username
        #         print("User is Authenticated")
            # if userHandler.login(username, password):
            #     verified_user = username
        # if user['auth_token'] != "":
        #     username, password = get_user(user)
        #     main_user = authenticate(username=username, password=password)
        #     print(main_user)
        #     if main_user is not None:
        #         verified_user = main_user.username
        #         print("User is Authenticated")
        # print("API keys", openai_api_key, prowritingaid_key)

        openai_api_key = get_default_openai_key(openai_api_key)
        prowritingaid_key = get_default_prowritingaid_key(prowritingaid_key)

        if verified_user is not None:
            # user_openai_key = userHandler.db.get_openai_key(username, password)
            # user_pwa_key    = userHandler.db.get_prowritingaidapi_key(username, password)
            d_user = DjangoUser.objects.get(username=username)
            print(d_user.username, d_user.extra)
            user_openai_key = d_user.extra.openai_api_key
            user_pwa_key = d_user.extra.prowritingaid_api_key
            if user_openai_key:
                openai_api_key = user_openai_key
            if user_pwa_key:
                prowritingaid_key = user_pwa_key

            if not openai_api_key:
                raise Exception(ResourceValues.openai_error_prefix + "API key missing")
            if not prowritingaid_key:
                raise Exception(ResourceValues.prowritingaid_prefix + "API key missing")

            rephrased_essay = process_essay(
                essay,
                approach,
                context,
                randomness,
                tone,
                difficulty,
                additional_adjectives,
                openai_api_key,
                prowritingaid_key,
                verified_user,
                model,
            )
            return {"rephrased_essay": rephrased_essay}
    except Exception as e:
        logging.exception("Error occured while rephrasing text")
        print(traceback.print_exc())
        return {"error": str(e)}


@app.post("/login")
def login(
    user: User = Body(
        embed=True,
    )
):
    try:
        username, password = user.username, user.password
        # userHandler.login(username, password)
        user = authenticate(username=username, password=password)
        if user is None:
            return {"error": "Invalid username` or password"}
        else:
            token_content = json.dumps({"username": username, "password": password})
            user_token = password_encrypt(
                token_content.encode(encoding="utf-8"), ResourceValues.token
            )
            return {"token": user_token}
    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}


@app.post("/api_keys")
def set_api_keys(
    user: User = Body(
        embed=True,
    ),
    api_config: APIConfig = Body(
        embed=True,
    ),
):
    try:
        oakey = api_config.openai_api_key
        oakey = oakey.strip() if type(oakey) == str else oakey
        pwakey = api_config.prowritingaid_api_key
        pwakey = pwakey.strip() if type(pwakey) == str else pwakey

        if DjangoUser.objects.filter(username=user.username).exists():
            authentication = authenticate(
                username=user.username, password=user.password
            )
            if authentication:
                d_user = UserExtraFields.objects.get(user__username=user.username)
                d_user.openai_api_key = oakey
                d_user.prowritingaid_api_key = pwakey
                d_user.save()
                return {
                    "success": "Set OpenAI keys and Prowritingaid api key successfully"
                }

        raise Exception("Invalid username or password")

        # db = Database(ResourceValues.database_file)
        # db.set_openai_key(username, password, oakey)
        # db.set_prowritingaidapi_key(username, password, pwakey)

    except Exception as e:
        return {"error": str(e)}


# User = get_user_model()


@app.post("/register")
def create_user(user: User = Body(embed=True)):
    try:
        # db = Database(ResourceValues.database_file)
        username, password = get_user(
            user, token_enabled=False
        )  # As we are registering disallow passing token
        if DjangoUser.objects.filter(username=username).exists():
            raise Exception("Username already exists")
        else:
            user = DjangoUser.objects.create_user(username=username, password=password)
            UserExtraFields.objects.create(user=user)
            return {"success": "Created user successfully"}
        # if db.username_exists(username):
        #     raise Exception("Username already exists")
        # if db.create_user(username, password):
        #     return {"success": "Created user successfully"}
        # else:
        #     raise Exception("Unknown error")
        # if db.username_exists(username):
        #     raise Exception("Username already exists")
    except Exception as e:
        print(traceback.print_exc())
        return {"error": str(e)}


# Stripe Endpoint


def create_order(session):
    print("Creating order")


def fulfill_order(session_response):
    session_id = session_response.get("id")
    print(session_id)
    session = stripe.checkout.Session.retrieve(session_id)
    print(session)

    metadata = session.get("metadata", {})
    if metadata:
        username = metadata["user-payment-uuid"]
        # db = Database(ResourceValues.database_file)

        subscription_id = session_response.get("subscription")

        user_fields = UserExtraFields.objects.get(user=username)
        user_fields.subscription_id = subscription_id
        user_fields.subscribed = True
        user_fields.save()
        # db.set_subscription_id(username, subscription_id)
        # db.subscribe_user(username)

        # plan_id = metadata["subscription-plan-uuid"]
        # print("UUID")
        # user_subscription = UserSubscription.objects.get(payment_uuid=user_payment_id)
        # print("Fulfilling order")
        # user_subscription.plan = SubscriptionPlan.objects.get(plan_id=plan_id)
        # user_subscription.last_paid_date = timezone.now()

        # user_subscription.is_active = True
        # user_subscription.save()

    else:
        print("no user payment uuid")
        logging.warning("No user paymeny uuid")


# def handle_subscription_cancelled(event):
#     subscription_id = event['data']['object']['id']
#     db = Database(ResourceValues.database_file)
#     user = db.get_user_from_subscription(subscription_id)
#     if user:
#         db.unsubscribe_user(user)


@app.post("/stripe/webhook")
async def stripe_webhook(
    request: Request, Stripe_Signature: Annotated[str | None, Header()] = None
):
    endpoint_secret = ResourceValues.stripe_wh_endpoint
    payload = await request.body()
    # print(payload)
    # print("*************")
    # print(request.headers)
    sig_header = Stripe_Signature

    # print(sig_header)
    # print(endpoint_secret)
    event = None

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        # print("****************")
        # print(event)
    except ValueError as e:
        # Invalid payload
        print(e)
        logging.exception("Exception occurred while validating payload of stripe API")
        return HTTPException(status_code=404, detail="URL not found")
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        print(e)
        logging.exception("Exception occurred while validating stripe API origin")
        return HTTPException(status_code=404, detail="URL not found")

    # Handle the checkout.session.completed event
    # if event['type'] == 'checkout.session.completed':
    #   session = event['data']['object']
    #
    #   # Fulfill the purchase...
    #   fulfill_order(session)
    # Handle the checkout.session.completed event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        # Save an order in your database, marked as 'awaiting payment'
        create_order(session)

        # Check if the order is already paid (for example, from a card payment)
        #
        # A delayed notification payment will have an `unpaid` status, as
        # you're still waiting for funds to be transferred from the customer's
        # account.
        if session.payment_status == "paid":
            # Fulfill the purchase
            fulfill_order(session)

    elif event["type"] == "checkout.session.async_payment_succeeded":
        session = event["data"]["object"]

        # Fulfill the purchase
        fulfill_order(session)

    elif event["type"] == "checkout.session.async_payment_failed":
        session = event["data"]["object"]
        # Send an email to the customer asking them to retry their order
        # email_customer_about_failed_payment(session)
    elif (
        event["type"] == "customer.subscription.deleted"
    ):  # Subscription has been cancelled
        print("Found deleted subscription")
        # Retrieve the subscription ID from the event data
        subscription_id = event["data"]["object"]["id"]
        print("Deleting ", subscription_id)
        try:
            user_f = UserExtraFields.objects.get(subscription_id=subscription_id)
            user_f.subscribed = False
            user_f.save()
        except Exception as e:
            print(e)
            logging.exception("Exception occurred while retrieving user")
            return HTTPException(status_code=404, detail="User not found")
        # unsubscribe_subscription(subscription_id)

    # Passed signature verification
    return HTTPException(status_code=200)
