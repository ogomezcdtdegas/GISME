from rest_framework import serializers
from .models import NodeRedData

class NodeRedDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = NodeRedData
        fields = '__all__'

