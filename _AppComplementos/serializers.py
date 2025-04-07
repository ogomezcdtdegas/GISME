from rest_framework import serializers
from .models import Criticidad, TipoCriticidad, Producto, TipoCriticidadCriticidad, ProductoTipoCritCrit

class CriticidadSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M", required=False, read_only=True)  

    class Meta:
        model = Criticidad
        fields = ["id", "name", "created_at"]  # 🔹 Agregar "id"

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

class ProductoTipoCriticiddadSerializer(serializers.ModelSerializer):
    tipo_criticidad_name = serializers.CharField(source="tipo_criticidad.name", read_only=True)
    producto_name = serializers.CharField(source="producto.name", read_only=True)

    class Meta:
        model = ProductoTipoCritCrit
        fields = ['id', 'producto', 'producto_name' 'tipo_criticidad', 'tipo_criticidad_name', 'criticidad', 'criticidad_name', 'created_at']
