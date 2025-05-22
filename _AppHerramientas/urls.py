from django.urls import path
from .views.views_fluxpro_propiedadesGas.Queries import CalcularPropiedadesGasQuery
from .views.views_fluxpro_velocidadSonido.Queries import CalcularVelocidadSonidoGasQuery

urlpatterns = [
    path("fluxpro/", CalcularPropiedadesGasQuery.FluxPro_view, name="fluxpro"),
    path("fluxproVel/", CalcularVelocidadSonidoGasQuery.FluxProVel_view, name="fluxproVel"),
    path("FluxCalcProp/", CalcularPropiedadesGasQuery.FluxCalcProp_view.as_view(), name="FluxCalcProp"),
]