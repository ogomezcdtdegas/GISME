from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),  # 📌 Ruta para la página de inicio
]
