from django.urls import path
from .views.views_fluxpro.views_fluxpro_propiedadesGas.Queries import CalcularPropiedadesGasQuery
from .views.views_fluxpro.views_fluxpro_velocidadSonido.Queries import CalcularVelocidadSonidoGasQuery
from .views.views_fluxpro.views_fluxpro_caudalMedLineal.Queries import CalcularCaudMedLinealQuery

urlpatterns = [
    # Controladores de redirección index.html
    path("fluxpro/", CalcularPropiedadesGasQuery.FluxPro_view, name="fluxpro"),
    path("fluxproVel/", CalcularVelocidadSonidoGasQuery.FluxProVel_view, name="fluxproVel"),
    path("fluxproCaudLineal/", CalcularCaudMedLinealQuery.FluxProCaudLineal_view, name="fluxproCaudLineal"),

    # Controladores de cálculo interno
    path("FluxCalcProp/", CalcularPropiedadesGasQuery.FluxCalcProp_view.as_view(), name="FluxCalcProp"),
    path("FluxCalcPropVel/", CalcularVelocidadSonidoGasQuery.FluxCalcProVel_view.as_view(), name="FluxCalcPropVel"),
    path("FluxCalcPropCaudLineal/", CalcularCaudMedLinealQuery.FluxCalcProCaudLineal_view.as_view(), name="FluxCalcPropCaudLineal"),
]