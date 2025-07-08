from django.contrib import admin
from .models import (
    TipoEquipo, Producto, TipoEquipoProducto, 
    TipoCriticidad, Criticidad, TipoCriticidadCriticidad,
    Tecnologia, TecnologiaTipoEquipo
)

# Register your models here.
@admin.register(TipoEquipo)
class TipoEquipoAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(TipoEquipoProducto)
class TipoEquipoProductoAdmin(admin.ModelAdmin):
    list_display = ('tipo_equipo', 'producto', 'created_at')
    list_filter = ('tipo_equipo', 'producto')

@admin.register(TipoCriticidad)
class TipoCriticidadAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(Criticidad)
class CriticidadAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(TipoCriticidadCriticidad)
class TipoCriticidadCriticidadAdmin(admin.ModelAdmin):
    list_display = ('tipo_criticidad', 'criticidad', 'created_at')
    list_filter = ('tipo_criticidad', 'criticidad')

@admin.register(Tecnologia)
class TecnologiaAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(TecnologiaTipoEquipo)
class TecnologiaTipoEquipoAdmin(admin.ModelAdmin):
    list_display = ('tecnologia', 'tipo_equipo_producto', 'tipo_criticidad_criticidad', 'created_at')
    list_filter = ('tecnologia', 'tipo_equipo_producto__tipo_equipo', 'tipo_criticidad_criticidad__tipo_criticidad')
