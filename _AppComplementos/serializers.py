from rest_framework import serializers
from .models import Ubicacion, Ubicacion, Sistema

'''xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'''
'''                                                   Serializer de Ubicacion                                                       '''
'''xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'''
class UbicacionSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M", required=False, read_only=True)
    
    class Meta:
        model = Ubicacion
        fields = ["id", "nombre", "latitud", "longitud", "created_at"]
        
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
    
    def get_ubicacion_coordenadas(self, obj):
        """Retorna las coordenadas de la ubicación como string"""
        if obj.ubicacion and obj.ubicacion.latitud is not None and obj.ubicacion.longitud is not None:
            return f"({obj.ubicacion.latitud}, {obj.ubicacion.longitud})"
        return "Sin coordenadas"
        
    def validate(self, attrs):
        """Validación a nivel de modelo para evitar duplicados"""
        tag = attrs.get('tag')
        sistema_id = attrs.get('sistema_id') 
        ubicacion = attrs.get('ubicacion')
        
        # Si estamos actualizando, excluir el objeto actual
        queryset = Sistema.objects.filter(tag=tag, sistema_id=sistema_id, ubicacion=ubicacion)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
            
        if queryset.exists():
            raise serializers.ValidationError(
                f"Ya existe un sistema con Tag '{tag}', ID '{sistema_id}' y ubicación '{ubicacion.nombre}'"
            )
        
        return attrs
        
    def validate_tag(self, value):
        """Validar que el tag no esté vacío y tenga formato correcto"""
        if not value or not value.strip():
            raise serializers.ValidationError("El Tag es obligatorio.")
        return value.strip()
    
    def validate_sistema_id(self, value):
        """Validar que el sistema_id no esté vacío"""
        if not value or not value.strip():
            raise serializers.ValidationError("El ID Sistema es obligatorio.")
        return value.strip()
'''xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'''