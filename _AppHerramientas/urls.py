from django.urls import path
from .views import FluxPro_view, FluxCalcProp_view

urlpatterns = [
    path("fluxpro/", FluxPro_view, name="fluxpro"),
    path("FluxCalcProp/", FluxCalcProp_view.as_view(), name="FluxCalcProp"),
]