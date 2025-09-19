from rest_framework import serializers
from .models import NodeRedData

class NodeRedDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = NodeRedData
        fields = [
            'id', 'tag_Sistema', 'volumen_total', 'volumen_fwd', 'volumen_rev',
            'masa_total', 'masa_fwd', 'masa_rev', 'densidad', 'volumen_60f',
            'grav_spec_60f', 'caudal_rate', 'mass_rate', 'temperatura_coriolis',
            'temperatura_diagnostico', 'temperatura_redundante', 'presion', 'created_at'
        ]
