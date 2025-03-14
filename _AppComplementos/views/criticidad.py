#from django.shortcuts import render, get_object_or_404
#from django.core.paginator import Paginator
#from rest_framework.views import APIView
#from rest_framework.response import Response
#from rest_framework import status

from repoGenerico.views_base import BaseListView, BaseCreateView, BaseRetrieveUpdateView
from ..models import Criticidad
from ..serializers import CriticidadSerializer


# 🔹 Listado paginado
class allCriticidadPag(BaseListView):
    model = Criticidad
    serializer_class = CriticidadSerializer
    template_name = "_AppComplementos/templates_criticidad/index.html"

# 🔹 Creación independiente
class crearCriticidad(BaseCreateView):
    model = Criticidad
    serializer_class = CriticidadSerializer

# 🔹 Edición
class editarCriticidad(BaseRetrieveUpdateView):
    model = Criticidad
    serializer_class = CriticidadSerializer