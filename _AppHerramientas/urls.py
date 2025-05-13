from django.urls import path
from .views import FluxPro_view

urlpatterns = [
    path("fluxpro/", FluxPro_view, name="fluxpro"),
]