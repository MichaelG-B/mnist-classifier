"""URL routes for the classifier app.  OWNER: Person C."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("classify/", views.classify, name="classify"),
    # TEMPORARY ALIAS: the templates on main still say {% url 'mock_result' %}
    # in base.html, home.html and result.html. This keeps every page working
    # until Person D's follow-up switches them to 'classify'.
    # DELETE THIS LINE once that change is merged.
    path("mock/", views.classify, name="mock_result"),
]
