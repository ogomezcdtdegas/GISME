from django.urls import path
from .views import IncertidumbreAPIView

urlpatterns = [
    path('incertidumbre/', IncertidumbreAPIView.as_view(), name='calcular_incertidumbre'),
]
