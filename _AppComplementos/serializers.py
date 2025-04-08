from rest_framework import serializers
from .models import Criticidad, TipoCriticidad, Producto, TipoCriticidadCriticidad, ProductoTipoCritCrit


'''xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'''
'''                                                   Serializer de Criticidad                                                      '''
'''xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'''
class CriticidadSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M", required=False, read_only=True)  

    class Meta:
        model = Criticidad
        fields = ["id", "name", "created_at"]  # 🔹 Agregar "id"
'''xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'''



'''xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'''
'''                                           Serializer de Tipo de Criticidad                                                      '''
'''xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'''
class TipoCriticidadSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M", required=False, read_only=True)  

    class Meta:
        model = TipoCriticidad
        fields = ["id", "name", "created_at"]  # 🔹 Agregar "id"

class TipoCriticidadCriticidadSerializer(serializers.ModelSerializer):
    tipo_criticidad_name = serializers.CharField(source="tipo_criticidad.name", read_only=True)
    criticidad_name = serializers.CharField(source="criticidad.name", read_only=True)

    class Meta:
        model = TipoCriticidadCriticidad
        fields = ['id', 'tipo_criticidad', 'tipo_criticidad_name', 'criticidad', 'criticidad_name', 'created_at']
'''xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'''



'''xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'''
'''                                                   Serializer de Producto                                                        '''
'''xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'''
class ProductoSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M", required=False, read_only=True)  

    class Meta:
        model = Producto
        fields = ["id", "name", "created_at"]  # 🔹 Agregar "id"

class ProductoTipoCriticiddadSerializer(serializers.ModelSerializer):
    producto_name = serializers.CharField(source='producto.name')
    tipo_criticidad_name = serializers.CharField(source='relacion_tipo_criticidad.tipo_criticidad.name')
    criticidad_name = serializers.CharField(source='relacion_tipo_criticidad.criticidad.name')
    tipo_criticidad_id = serializers.UUIDField(source='relacion_tipo_criticidad.tipo_criticidad.id')
    
    class Meta:
        model = ProductoTipoCritCrit
        fields = ['id', 'producto_name', 'tipo_criticidad_name', 'criticidad_name', 'tipo_criticidad_id']

class CriticidadesPorTipoSerializer(serializers.ModelSerializer):
    value = serializers.UUIDField(source='criticidad.id')  # Cambiado a UUIDField
    label = serializers.CharField(source='criticidad.name')

    class Meta:
        model = TipoCriticidadCriticidad
        fields = ['value', 'label']
'''xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'''