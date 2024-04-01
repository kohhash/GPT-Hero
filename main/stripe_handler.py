import stripe
# from .models import Essays
from accounts.models import UserExtraFields

def cancel_subscription(subscription_id):
    print("Cancelling subscription", subscription_id)
    try:
        subscription = stripe.Subscription.retrieve(subscription_id)
        print(subscription)
        # subscription.delete()
        stripe.Subscription.cancel(subscription_id)
        userObj=UserExtraFields.objects.get(subscription_id=subscription_id)
        setattr(userObj, 'subscribed', False)
        userObj.save()
        setattr(userObj, 'openai_api_key', None)
        userObj.save()
        setattr(userObj, 'prowritingaid_api_key', None)
        userObj.save()
        return True
    except stripe.error.StripeError as e:
        # Handle any errors that occur during the cancellation process
        print(f"Error canceling subscription: {e}")
        return False

def stripe_purchase_url(username):
    checkout_session = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[
            {
                # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                "price": "price_1NCwPzImNVsu0Keipoc1BpMM",
            },
        ],
        success_url="http://localhost:8000/profile?id={CHECKOUT_SESSION_ID}",
        metadata={"user-payment-uuid": username},
        cancel_url="http://localhost:8000/failure",
    )

    return checkout_session.url


def stripe_special_purchase_url(username):
    special_checkout_session = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[
            {
                # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                "price": "price_1NCwPzImNVsu0Keipoc1BpMM",
            },
        ],
        success_url="http://localhost:8000/profile?id={CHECKOUT_SESSION_ID}",
        metadata={"user-payment-uuid": username},
        cancel_url="http://localhost:8000/failure",
    )

    return special_checkout_session.url