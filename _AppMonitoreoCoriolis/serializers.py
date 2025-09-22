from rest_framework import serializers
from .models import NodeRedData

class NodeRedDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = NodeRedData
        fields = [
            'id', 'tag_system', 'total_volume', 'forward_volume', 'reverse_volume',
            'total_mass', 'forward_mass', 'reverse_mass', 'density', 'volume_60f',
            'specific_gravity_60f', 'flow_rate', 'mass_rate', 'coriolis_temperature',
            'diagnostic_temperature', 'redundant_temperature', 'pressure', 'created_at'
        ]

