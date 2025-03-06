from django.urls import path
from . import views

urlpatterns = [
    #path('', views.index, name='calc1'),  # 📌 URL de Calc1
    path("", views.calc1_view, name="calc1"),
]