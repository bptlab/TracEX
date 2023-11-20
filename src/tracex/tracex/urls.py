from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("extraction/", include("extraction.urls")),
    path("admin/", admin.site.urls),
]
