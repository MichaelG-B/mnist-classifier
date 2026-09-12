"""Project-wide URL routes.  OWNER: Person C."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # Django's built-in auth: login, logout, password change.
    # It deliberately provides NO signup route, which is requirement 1b.
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("classifier.urls")),
]
