from rest_framework import serializers
from .models import Criticidad, TipoCriticidad

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
