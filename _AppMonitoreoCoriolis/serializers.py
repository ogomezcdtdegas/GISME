from rest_framework import serializers
from .models import NodeRedData

class NodeRedDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = NodeRedData
        fields = ['id', 'sensor', 'valor', 'created_at']
