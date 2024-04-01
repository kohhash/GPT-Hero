from django.urls import path
from .views import hide_and_show_api_keys , login_for_migration_user

urlpatterns = [
        path("hide_and_show_api_keys/", hide_and_show_api_keys, name="hide_and_show_api_keys"),
        path("login_migrate/", login_for_migration_user, name="login_for_migration_user"),
]
