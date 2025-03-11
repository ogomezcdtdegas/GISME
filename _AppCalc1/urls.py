from django.urls import path
from .views import calc1_view

urlpatterns = [
    path("calc1/", calc1_view.as_view(), name="calc1"),
]