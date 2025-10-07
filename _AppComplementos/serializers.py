from rest_framework import serializers
from .models import Ubicacion, Ubicacion, Sistema, ConfiguracionCoeficientes, ConfiguracionCoeficientes

'''xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'''
'''                                                   Serializer de Ubicacion                                                       '''
'''xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'''
class UbicacionSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M", required=False, read_only=True)
    
    class Meta:
        model = Ubicacion
        fields = ["id", "nombre", "latitud", "longitud", "created_at"]
        extra_kwargs = {
            'nombre': {'validators': []},  # Desactivar validadores automáticos
        }
        
    def validate_nombre(self, value):
        """Validar que el nombre no esté vacío y sea único"""
        if not value or not value.strip():
            raise serializers.ValidationError("El nombre de ubicación es obligatorio.")
        
        value = value.strip()
        
        # Validar unicidad del nombre
        queryset = Ubicacion.objects.filter(nombre=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError("Ya existe una ubicación con este nombre.")
        
        return value
        
    def validate_latitud(self, value):
        """Validar que la latitud esté en el rango correcto"""
        if value < -90 or value > 90:
            raise serializers.ValidationError("La latitud debe estar entre -90 y 90 grados.")
        return value
    
    def validate_longitud(self, value):
        """Validar que la longitud esté en el rango correcto"""
        if value < -180 or value > 180:
            raise serializers.ValidationError("La longitud debe estar entre -180 y 180 grados.")
        return value
'''xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'''

'''xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'''
'''                                                   Serializer de Sistema                                                         '''
'''xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'''
class SistemaSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M", required=False, read_only=True)
    ubicacion_nombre = serializers.CharField(source="ubicacion.nombre", read_only=True)
    ubicacion_lat = serializers.DecimalField(source="ubicacion.latitud", max_digits=10, decimal_places=7, read_only=True)
    ubicacion_lng = serializers.DecimalField(source="ubicacion.longitud", max_digits=10, decimal_places=7, read_only=True)
    ubicacion_coordenadas = serializers.SerializerMethodField()
    
    class Meta:
        model = Sistema
        fields = ["id", "tag", "sistema_id", "ubicacion", "ubicacion_nombre", "ubicacion_lat", "ubicacion_lng", "ubicacion_coordenadas", "created_at"]
        extra_kwargs = {
            'tag': {'validators': []},  # Desactivar validadores automáticos
            'sistema_id': {'validators': []},  # Desactivar validadores automáticos
        }
    
    def get_ubicacion_coordenadas(self, obj):
        """Retorna las coordenadas de la ubicación como string"""
        if obj.ubicacion and obj.ubicacion.latitud is not None and obj.ubicacion.longitud is not None:
            return f"({obj.ubicacion.latitud}, {obj.ubicacion.longitud})"
        return "Sin coordenadas"
        
    def validate(self, attrs):
        """Validación general a nivel de modelo"""
        # Las validaciones de unicidad están en validate_tag y validate_sistema_id
        # Aquí solo validaciones adicionales si las necesitamos
        return attrs
        
    def validate_tag(self, value):
        """Validar que el tag no esté vacío y sea único"""
        if not value or not value.strip():
            raise serializers.ValidationError("El Nombre es obligatorio.")
        
        value = value.strip()
        
        # Validar unicidad del tag
        queryset = Sistema.objects.filter(tag=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError("Ya existe un sistema con este Nombre.")
        
        return value
    
    def validate_sistema_id(self, value):
        """Validar que el sistema_id no esté vacío y sea único"""
        if not value or not value.strip():
            raise serializers.ValidationError("El MAC Gateway es obligatorio.")
        
        value = value.strip()
        
        # Validar unicidad del sistema_id
        queryset = Sistema.objects.filter(sistema_id=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError("Ya existe un sistema con este MAC Gateway.")
        
        return value
'''xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'''

'''xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'''
'''                                           Serializer de ConfiguracionCoeficientes                                              '''
'''xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'''
class ConfiguracionCoeficientesSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M", required=False, read_only=True)
    sistema_tag = serializers.CharField(source="systemId.tag", read_only=True)
    sistema_nombre = serializers.SerializerMethodField()
    
    class Meta:
        model = ConfiguracionCoeficientes
        fields = ["id", "systemId", "sistema_tag", "sistema_nombre", "mt", "bt", "mp", "bp", 
                 "zero_presion", "span_presion", "lim_inf_caudal_masico", "lim_sup_caudal_masico", 
                 "vol_masico_ini_batch", "created_at"]
    
    def get_sistema_nombre(self, obj):
        """Retorna el nombre completo del sistema"""
        if obj.systemId:
            return f"{obj.systemId.tag} - {obj.systemId.sistema_id}"
        return "Sin sistema"
'''xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'''