from django.contrib import admin
from .models import (
    Ubicacion, Sistema
)

# Register your models here.

@admin.register(Ubicacion)
class UbicacionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'latitud', 'longitud', 'created_at')
    search_fields = ('nombre',)
    list_filter = ('created_at',)

@admin.register(Sistema)
class SistemaAdmin(admin.ModelAdmin):
    list_display = ('tag', 'sistema_id', 'ubicacion', 'created_at')
    search_fields = ('tag', 'sistema_id', 'ubicacion__nombre')
    list_filter = ('ubicacion', 'created_at')
    autocomplete_fields = ('ubicacion',)
