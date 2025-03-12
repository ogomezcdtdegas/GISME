from rest_framework import serializers
from .models import Equipo

class EquipoSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M", required=False, read_only=True)  # 🔹 Ahora es opcional y solo de lectura

    class Meta:
        model = Equipo
        fields = ["serial", "sap", "marca", "created_at"]
