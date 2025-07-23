from repoGenerico.views_base import BaseRetrieveUpdateView, BaseReadForIdView
from .....models import Producto, ProductoTipoCritCrit, TipoCriticidadCriticidad
from .....serializers import ProductoTipoCriticiddadSerializer
from django.http import JsonResponse
from django.db import transaction
from rest_framework import status

from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    put=extend_schema(tags=['Producto']),
    patch=extend_schema(tags=['Producto']),
)

class EditarProductoView(BaseRetrieveUpdateView, BaseReadForIdView):
    model = ProductoTipoCritCrit
    serializer_class = ProductoTipoCriticiddadSerializer

    def get(self, request, obj_id):
        """ Vista GET para obtener los datos de un producto para edición """
        try:
            relacion = self.get_object_by_id(ProductoTipoCritCrit, obj_id, "Producto no encontrado")
            serializer = self.serializer_class(relacion)
            return JsonResponse({"success": True, "data": serializer.data}, status=200)
        except ValueError as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)
        except Exception as e:
            return JsonResponse({"success": False, "error": f"Error inesperado: {str(e)}"}, status=500)

    def put(self, request, *args, **kwargs):
        producto_id = kwargs.get("obj_id")
        data = request.data

        if not producto_id:
            return JsonResponse({'success': False, 'error': 'ID de producto requerido'}, status=400)

        # Validar que todos los campos requeridos estén presentes
        nuevo_nombre = data.get('name')
        nuevo_tipo_criticidad_id = data.get('tipo_criticidad_id')
        nueva_criticidad_id = data.get('criticidad_id')

        if not all([nuevo_nombre, nuevo_tipo_criticidad_id, nueva_criticidad_id]):
            return JsonResponse({
                'success': False, 
                'error': 'Todos los campos son obligatorios (name, tipo_criticidad_id, criticidad_id)'
            }, status=400)

        try:
            with transaction.atomic():  # Usar transacción para consistencia
                # 1. Obtener producto actual y sus datos
                relacion_actual = self.get_object_by_id(ProductoTipoCritCrit, producto_id, "Producto no existe")
                producto_actual = relacion_actual.producto

                # Datos del formulario ya validados arriba

                # 2. Verificar que la combinación tipo-criticidad existe
                try:
                    nueva_relacion_tipo_crit = TipoCriticidadCriticidad.objects.get(
                        tipo_criticidad_id=nuevo_tipo_criticidad_id,
                        criticidad_id=nueva_criticidad_id
                    )
                except TipoCriticidadCriticidad.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'error': 'La combinación de tipo y criticidad no es válida'
                    }, status=400)

                # 3. Verificar si ya existe otro producto con esta combinación
                existe_combinacion = ProductoTipoCritCrit.objects.filter(
                    producto__name=nuevo_nombre,
                    relacion_tipo_criticidad=nueva_relacion_tipo_crit
                ).exclude(producto_id=producto_actual.id).exists()

                if existe_combinacion:
                    return JsonResponse({
                        'success': False,
                        'error': 'Ya existe un producto con esta combinación de tipo y criticidad'
                    }, status=400)

                # 4. Actualizar el producto
                if nuevo_nombre != producto_actual.name:
                    producto_actual.name = nuevo_nombre
                    producto_actual.save()

                # 5. Actualizar la relación
                cambios = []
                if (relacion_actual.relacion_tipo_criticidad_id != nueva_relacion_tipo_crit.id):
                    relacion_actual.relacion_tipo_criticidad = nueva_relacion_tipo_crit
                    cambios.append("Se actualizó la relación tipo-criticidad")
                
                relacion_actual.save()

                return JsonResponse({
                    'success': True,
                    'message': 'Producto actualizado correctamente',
                    'cambios': [
                        f"Nombre actualizado: {nuevo_nombre}" if nuevo_nombre != producto_actual.name else None,
                        *cambios
                    ]
                }, status=200)

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)