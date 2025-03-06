
from django.urls import path
from .views import  calcular_incertidumbre

urlpatterns = [
    #path('incertidumbre/', formulario_incertidumbre, name='formulario_incertidumbre'),
    path('incertidumbre/', calcular_incertidumbre, name='calcular_incertidumbre'),  # 🔹 API SOLO PARA POST
]