from repoGenerico.views_base import BaseCreateView
from rest_framework.response import Response
from rest_framework import status
from .....models import Producto, ProductoTipoCritCrit, TipoCriticidadCriticidad
from .....serializers import ProductoTipoCriticiddadSerializer
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    post=extend_schema(tags=['Producto']),
)
class CrearProductoCompletoView(BaseCreateView):
    """
    Vista para crear un producto con su relación completa de tipo y criticidad
    Requiere:
    - name: nombre del producto
    - tipo_criticidad_id: UUID del tipo de criticidad
    - criticidad_id: UUID de la criticidad
    """
    
    def post(self, request):
        data = request.data
        producto_name = data.get('name')
        tipo_criticidad_id = data.get('tipo_criticidad_id')
        criticidad_id = data.get('criticidad_id')

        # Validación básica
        if not all([producto_name, tipo_criticidad_id, criticidad_id]):
            return Response(
                {'success': False, 'message': 'Todos los campos son obligatorios'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # 1. Verificar que exista la relación TipoCriticidad-Criticidad
            relacion_tipo_crit = get_object_or_404(
                TipoCriticidadCriticidad,
                tipo_criticidad_id=tipo_criticidad_id,
                criticidad_id=criticidad_id
            )

            # 2. Crear o obtener el producto
            producto, _ = Producto.objects.get_or_create(name=producto_name)

            # 3. Crear la relación completa
            relacion_producto, created = ProductoTipoCritCrit.objects.get_or_create(
                producto=producto,
                relacion_tipo_criticidad=relacion_tipo_crit,
                defaults={
                    'created_at': request.user if request.user.is_authenticated else None
                }
            )

            if not created:
                return Response(
                    {"success": False, "message": "Esta combinación de producto y criticidad ya existe"},
                    status=status.HTTP_200_OK
                )

            # 4. Retornar respuesta con datos serializados
            serializer = ProductoTipoCriticiddadSerializer(relacion_producto)
            return Response(
                {
                    "success": True,
                    "message": "Producto creado exitosamente",
                    "data": serializer.data
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                {"success": False, "message": f"Error al crear producto: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )