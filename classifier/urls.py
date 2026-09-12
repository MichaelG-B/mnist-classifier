"""URL routes for the classifier app.  OWNER: Person C."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    # TEMPORARY: Person D builds the result page against this.
    # Person C deletes this route on integration day.
    path("mock/", views.mock_result, name="mock_result"),
]
