"""tracex URL Configuration for tracex app"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("", include("patient_journey_generator.urls")),
    path("", include("extraction.urls")),
    path("", include("event_log_testing_env.urls")),
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
