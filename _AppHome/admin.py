from django.contrib import admin

from .models import Equipo  # Importa el modelo

@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = ('serial', 'sap', 'marca', 'created_at')  # Campos visibles en la lista
    search_fields = ('serial', 'sap', 'marca')  # Agrega barra de búsqueda
    list_filter = ('marca',)  # Agrega filtros por marca
    ordering = ('-created_at',)  # Ordena por fecha de creación (más recientes primero)