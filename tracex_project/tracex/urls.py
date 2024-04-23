"""tracex URL Configuration for tracex app"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("", include("patient_journey_generator.urls")),
    path("set-api-key/", views.set_api_key, name="set_api_key"),
    path("", include("extraction.urls")),
    path("", include("trace_comparator.urls")),
    path("", views.TracexLandingPage.as_view(), name="landing_page"),
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
