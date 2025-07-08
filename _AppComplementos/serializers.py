from rest_framework import serializers
from .models import Criticidad, TipoCriticidad, Producto, TipoCriticidadCriticidad, ProductoTipoCritCrit, TipoEquipo, TipoEquipoProducto, Tecnologia, TecnologiaTipoEquipo, Tecnologia, TecnologiaTipoEquipo


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
    tipo_criticidad_id = serializers.UUIDField(source="tipo_criticidad.id", read_only=True)
    total_relations = serializers.IntegerField(read_only=True)

    def get_total_relations_fallback(self, obj):
        """Método de respaldo en caso de que no haya anotación"""
        if hasattr(obj, 'total_relations'):
            return obj.total_relations
        return ProductoTipoCritCrit.objects.filter(relacion_tipo_criticidad=obj).count()
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Si no hay anotación, usar el método de respaldo
        if not hasattr(instance, 'total_relations') or instance.total_relations is None:
            data['total_relations'] = self.get_total_relations_fallback(instance)
        return data

    class Meta:
        model = TipoCriticidadCriticidad
        fields = ['id', 'tipo_criticidad', 'tipo_criticidad_id', 'tipo_criticidad_name', 'criticidad', 'criticidad_name', 'created_at', 'total_relations']



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
    criticidad_id = serializers.UUIDField(source='relacion_tipo_criticidad.criticidad.id')
    producto_id = serializers.UUIDField(source='producto.id')
    total_relations = serializers.IntegerField(read_only=True)

    def get_total_relations_fallback(self, obj):
        """Método de respaldo en caso de que no haya anotación"""
        if hasattr(obj, 'total_relations'):
            return obj.total_relations
        return ProductoTipoCritCrit.objects.filter(producto=obj.producto).count()
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Si no hay anotación, usar el método de respaldo
        if not hasattr(instance, 'total_relations') or instance.total_relations is None:
            data['total_relations'] = self.get_total_relations_fallback(instance)
        return data
    
    class Meta:
        model = ProductoTipoCritCrit
        fields = ['id', 'producto_id', 'producto_name', 'tipo_criticidad_name', 'criticidad_name', 'tipo_criticidad_id', 'criticidad_id', 'total_relations']

class CriticidadesPorTipoSerializer(serializers.ModelSerializer):
    value = serializers.UUIDField(source='criticidad.id')  # Cambiado a UUIDField
    label = serializers.CharField(source='criticidad.name')

    class Meta:
        model = TipoCriticidadCriticidad
        fields = ['value', 'label']
'''xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'''

'''xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'''
'''                                                Serializer de Tipo de Equipo                                                     '''
'''xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'''
class TipoEquipoSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M", required=False, read_only=True)  

    class Meta:
        model = TipoEquipo
        fields = ["id", "name", "created_at"]

class TipoEquipoProductoSerializer(serializers.ModelSerializer):
    tipo_equipo_name = serializers.CharField(source='tipo_equipo.name')
    producto_name = serializers.CharField(source='relacion_producto.producto.name')
    tipo_criticidad_name = serializers.CharField(source='relacion_producto.relacion_tipo_criticidad.tipo_criticidad.name')
    criticidad_name = serializers.CharField(source='relacion_producto.relacion_tipo_criticidad.criticidad.name')
    tipo_equipo_id = serializers.UUIDField(source='tipo_equipo.id')
    producto_id = serializers.UUIDField(source='relacion_producto.producto.id')
    tipo_criticidad_id = serializers.UUIDField(source='relacion_producto.relacion_tipo_criticidad.tipo_criticidad.id')
    criticidad_id = serializers.UUIDField(source='relacion_producto.relacion_tipo_criticidad.criticidad.id')
    total_relations = serializers.IntegerField(read_only=True)

    def get_total_relations_fallback(self, obj):
        """Método de respaldo en caso de que no haya anotación"""
        if hasattr(obj, 'total_relations'):
            return obj.total_relations
        return TipoEquipoProducto.objects.filter(tipo_equipo=obj.tipo_equipo).count()
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Si no hay anotación, usar el método de respaldo
        if not hasattr(instance, 'total_relations') or instance.total_relations is None:
            data['total_relations'] = self.get_total_relations_fallback(instance)
        return data
    
    class Meta:
        model = TipoEquipoProducto
        fields = ['id', 'tipo_equipo_id', 'tipo_equipo_name', 'producto_id', 'producto_name', 
                 'tipo_criticidad_name', 'criticidad_name', 'tipo_criticidad_id', 'criticidad_id', 'total_relations']
'''xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'''

'''xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'''
'''                                                   Serializer de Tecnología                                                       '''
'''xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'''
class TecnologiaSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M", required=False, read_only=True)  

    class Meta:
        model = Tecnologia
        fields = ["id", "name", "created_at"]

class TecnologiaTipoEquipoSerializer(serializers.ModelSerializer):
    tecnologia_name = serializers.CharField(source='tecnologia.name', read_only=True)
    tipo_equipo_name = serializers.CharField(source='relacion_tipo_equipo.tipo_equipo.name', read_only=True)
    producto_name = serializers.CharField(source='relacion_tipo_equipo.relacion_producto.producto.name', read_only=True)
    tipo_criticidad_name = serializers.CharField(source='relacion_tipo_equipo.relacion_producto.relacion_tipo_criticidad.tipo_criticidad.name', read_only=True)
    criticidad_name = serializers.CharField(source='relacion_tipo_equipo.relacion_producto.relacion_tipo_criticidad.criticidad.name', read_only=True)
    
    tecnologia_id = serializers.UUIDField(source='tecnologia.id')
    tipo_equipo_id = serializers.UUIDField(source='relacion_tipo_equipo.tipo_equipo.id')
    producto_id = serializers.UUIDField(source='relacion_tipo_equipo.relacion_producto.producto.id')
    tipo_criticidad_id = serializers.UUIDField(source='relacion_tipo_equipo.relacion_producto.relacion_tipo_criticidad.tipo_criticidad.id')
    criticidad_id = serializers.UUIDField(source='relacion_tipo_equipo.relacion_producto.relacion_tipo_criticidad.criticidad.id')
    total_relations = serializers.IntegerField(read_only=True)

    def get_total_relations_fallback(self, obj):
        """Método de respaldo en caso de que no haya anotación"""
        if hasattr(obj, 'total_relations'):
            return obj.total_relations
        return TecnologiaTipoEquipo.objects.filter(tecnologia=obj.tecnologia).count()
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Si no hay anotación, usar el método de respaldo
        if not hasattr(instance, 'total_relations') or instance.total_relations is None:
            data['total_relations'] = self.get_total_relations_fallback(instance)
        return data
    
    class Meta:
        model = TecnologiaTipoEquipo
        fields = ['id', 'tecnologia_id', 'tecnologia_name', 'tipo_equipo_id', 'tipo_equipo_name', 'producto_id', 'producto_name', 
                 'tipo_criticidad_name', 'criticidad_name', 'tipo_criticidad_id', 'criticidad_id', 'total_relations']