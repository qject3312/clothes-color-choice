from django.urls import path

from . import views

app_name = "django_dashboard"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("health/", views.health, name="health"),
]
