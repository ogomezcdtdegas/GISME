from rest_framework import serializers
from .models import Criticidad, TipoCriticidad, Producto, TipoCriticidadCriticidad, ProductoTipoCritCrit, TipoEquipo, TipoEquipoProducto, Tecnologia, TecnologiaTipoEquipo, Tecnologia, TecnologiaTipoEquipo, Ubicacion, Ubicacion, Sistema


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
        return TipoCriticidadCriticidad.objects.filter(tipo_criticidad=obj.tipo_criticidad).count()
    
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
'''xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'''

'''xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'''
'''                                                   Serializer de Ubicacion                                                       '''
'''xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'''
class UbicacionSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M", required=False, read_only=True)
    
    class Meta:
        model = Ubicacion
        fields = ["id", "nombre", "latitud", "longitud", "created_at"]
        
    def validate_latitud(self, value):
        """Validar que la latitud esté en el rango correcto"""
        if value < -90 or value > 90:
            raise serializers.ValidationError("La latitud debe estar entre -90 y 90 grados.")
        return value
    
    def validate_longitud(self, value):
        """Validar que la longitud esté en el rango correcto"""
        if value < -180 or value > 180:
            raise serializers.ValidationError("La longitud debe estar entre -180 y 180 grados.")
        return value
'''xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'''

'''xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'''
'''                                                   Serializer de Sistema                                                         '''
'''xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'''
class SistemaSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M", required=False, read_only=True)
    ubicacion_nombre = serializers.CharField(source="ubicacion.nombre", read_only=True)
    ubicacion_coordenadas = serializers.SerializerMethodField()
    
    class Meta:
        model = Sistema
        fields = ["id", "tag", "sistema_id", "ubicacion", "ubicacion_nombre", "ubicacion_coordenadas", "created_at"]
    
    def get_ubicacion_coordenadas(self, obj):
        """Retorna las coordenadas de la ubicación como string"""
        if obj.ubicacion and obj.ubicacion.latitud is not None and obj.ubicacion.longitud is not None:
            return f"({obj.ubicacion.latitud}, {obj.ubicacion.longitud})"
        return "Sin coordenadas"
        
    def validate(self, attrs):
        """Validación a nivel de modelo para evitar duplicados"""
        tag = attrs.get('tag')
        sistema_id = attrs.get('sistema_id') 
        ubicacion = attrs.get('ubicacion')
        
        # Si estamos actualizando, excluir el objeto actual
        queryset = Sistema.objects.filter(tag=tag, sistema_id=sistema_id, ubicacion=ubicacion)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
            
        if queryset.exists():
            raise serializers.ValidationError(
                f"Ya existe un sistema con Tag '{tag}', ID '{sistema_id}' y ubicación '{ubicacion.nombre}'"
            )
        
        return attrs
        
    def validate_tag(self, value):
        """Validar que el tag no esté vacío y tenga formato correcto"""
        if not value or not value.strip():
            raise serializers.ValidationError("El Tag es obligatorio.")
        return value.strip()
    
    def validate_sistema_id(self, value):
        """Validar que el sistema_id no esté vacío"""
        if not value or not value.strip():
            raise serializers.ValidationError("El ID Sistema es obligatorio.")
        return value.strip()
'''xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'''