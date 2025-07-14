from django.contrib import admin
from .models import (
    TipoEquipo, Producto, TipoEquipoProducto, 
    TipoCriticidad, Criticidad, TipoCriticidadCriticidad,
    Tecnologia, TecnologiaTipoEquipo, Ubicacion, Sistema
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
    list_display = ('tipo_equipo', 'relacion_producto', 'created_at')
    list_filter = ('tipo_equipo', 'relacion_producto__producto')

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
    list_display = ('tecnologia', 'relacion_tipo_equipo', 'created_at')
    list_filter = ('tecnologia', 'relacion_tipo_equipo__tipo_equipo')

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
