from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # path("app/", include("app.urls")),
    path("", include("main.urls")),
    path("account/", include("accounts.urls")),
    path('accounts/', include('allauth.urls')),
    path('admin/', admin.site.urls),
]

# write code when debug is False
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
