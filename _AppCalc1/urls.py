from django.urls import path
from . import views

urlpatterns = [
    # 📌 Ruta para la página de inicio
    path('calc1/', views.indexCalc1, name='calc1'),
]
