"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    #path('', include('_AppHome.urls')),  # Incluir las URLs de Home
    path('', include('_AppHome.urls')),  # Incluir las URLs de Home
    path('monitoreo/', include('_AppMonitoreoCoriolis.urls')),  # Incluir las URLs de Monitoreo
    path('complementos/', include('_AppComplementos.urls')),  # Incluir las URLs de Complementos
    path('herramientas/', include('_AppHerramientas.urls')),  # Incluir las URLs de Heramientas
    path('calc1/', include('_AppCalc1.urls')),  # Ruta para Calc1
    path('calc2/', include('_AppCalc2.urls')),  # Ruta para Calc2
    path('auth/', include('_AppAuth.urls')),    # Ruta para Auth
    path('admin_panel/', include('_AppAdmin.urls')), #Ruta para panel de administración
]
