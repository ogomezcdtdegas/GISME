from django.urls import path
from . import views

urlpatterns = [
<<<<<<< HEAD
    # 📌 Ruta para la página de inicio
    path('calc1/', views.indexCalc1, name='calc1'),
]
=======
    path('', views.index, name='calc1'),  # 📌 URL de Calc1
]
>>>>>>> origin/main
