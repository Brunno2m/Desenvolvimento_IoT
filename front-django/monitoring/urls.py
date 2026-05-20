from django.urls import path

from . import views


urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("api/state/", views.api_state, name="api_state"),
    path("api/command/", views.api_command, name="api_command"),
]
