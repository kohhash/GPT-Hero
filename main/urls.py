from django.urls import path
from . import views


urlpatterns = [
    path("", views.landing_view, name="landing"),
    path("home", views.home_view, name="home"),
    path("rephrase/<int:id>/", views.rephase_essay_view, name="rephrase"),
    path("history/", views.history_page_view, name="history"),
    path("profile/", views.profile_view, name="profile"),
    path("logout_redirect/", views.logout_redirect_view, name="logout_redirect"),
    path("cancel_sub/<str:id>/", views.cancel_sub, name="cancel_sub"),
    path("plans/", views.plans_page_view, name="plans"),
    path('plans/<int:pk>/', views.payment_post, name='plans_buy'),
	path('payment_successful/', views.payment_successful, name='payment_successful'),
	path('payment_cancelled/', views.payment_cancelled, name='payment_cancelled'),
	path('stripe_webhook/', views.stripe_webhook, name='stripe_webhook'),
]