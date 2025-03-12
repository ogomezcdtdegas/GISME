from rest_framework import serializers
from .models import Equipo

class EquipoSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M", required=False, read_only=True)  

    class Meta:
        model = Equipo
        fields = ["id", "serial", "sap", "marca", "created_at"]  # 🔹 Agregar "id"
