from django.urls import path
from django.views.generic import TemplateView

# URLs para páginas estáticas de _AppHome
urlpatterns = [
    path('', TemplateView.as_view(template_name='_AppHome/index.html'), name='home_index'),  # Página principal estática
]
