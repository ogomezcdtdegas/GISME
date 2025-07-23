from repoGenerico.views_base import BaseRetrieveUpdateView, BaseReadForIdView
from .....models import TipoCriticidadCriticidad, TipoCriticidad
from .....serializers import TipoCriticidadCriticidadSerializer
from django.http import JsonResponse
from rest_framework import status

from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    put=extend_schema(tags=['TipoCriticidad']),
    patch=extend_schema(tags=['TipoCriticidad']),
)

class editarTipCriticidad(BaseRetrieveUpdateView, BaseReadForIdView):  
    model = TipoCriticidadCriticidad
    serializer_class = TipoCriticidadCriticidadSerializer

    def put(self, request, *args, **kwargs):
        relacion_id = kwargs.get("obj_id")
        data = request.data

        if not relacion_id:
            return JsonResponse({'success': False, 'error': 'ID de relación requerido'}, status=400)

        try:
            relacion_actual = self.get_object_by_id(TipoCriticidadCriticidad, relacion_id, "Relación no existe")
            tipo_criticidad_actual = relacion_actual.tipo_criticidad  # Objeto TipoCriticidad actual
            criticidad_id_actual = relacion_actual.criticidad_id

            # Datos del formulario
            nuevo_nombre = data.get('name', tipo_criticidad_actual.name)
            nueva_criticidad_id = data.get('criticidad_id', criticidad_id_actual)

            # --- 1. Verificar si el nombre ya existe en otro TipoCriticidad ---
            tipo_criticidad_existente = TipoCriticidad.objects.filter(name=nuevo_nombre).exclude(id=tipo_criticidad_actual.id).first()

            if tipo_criticidad_existente:
                # --- Caso: El nombre existe en otro registro ---
                # Verificar si la relación M:N ya existe con el TipoCriticidad existente
                if TipoCriticidadCriticidad.objects.filter(
                    tipo_criticidad_id=tipo_criticidad_existente.id,
                    criticidad_id=nueva_criticidad_id
                ).exists():
                    return JsonResponse({
                        'success': False,
                        'error': 'Esta combinación (nombre + criticidad) ya existe.'
                    }, status=400)
                
                # --- Si no existe la relación, actualizar la tabla intermedia ---
                relacion_actual.tipo_criticidad = tipo_criticidad_existente  # 🔄 Usar el TipoCriticidad existente
                relacion_actual.criticidad_id = nueva_criticidad_id
                relacion_actual.save()

                return JsonResponse({
                    'success': True,
                    'message': 'Se asoció al TipoCriticidad existente y se actualizó la relación.',
                    'cambios': [
                        f"TipoCriticidad reasignado: {tipo_criticidad_existente.id}",
                        f"Criticidad actualizada: {nueva_criticidad_id}"
                    ]
                }, status=200)

            else:
                # --- Caso: El nombre NO existe en otro registro (o es el mismo) ---
                # Validar cambios en el nombre (si es diferente)
                if nuevo_nombre != tipo_criticidad_actual.name:
                    tipo_criticidad_actual.name = nuevo_nombre
                    tipo_criticidad_actual.save()

                # Validar cambios en la criticidad (si es diferente)
                if str(nueva_criticidad_id) != str(criticidad_id_actual):
                    if TipoCriticidadCriticidad.objects.filter(
                        tipo_criticidad_id=tipo_criticidad_actual.id,
                        criticidad_id=nueva_criticidad_id
                    ).exists():
                        return JsonResponse({
                            'success': False,
                            'error': 'Esta combinación (nombre + criticidad) ya existe.'
                        }, status=400)
                    
                    relacion_actual.criticidad_id = nueva_criticidad_id
                    relacion_actual.save()

                return JsonResponse({
                    'success': True,
                    'message': 'Actualizado correctamente.',
                    'cambios': [
                        f"Nombre actualizado: {nuevo_nombre}" if nuevo_nombre != tipo_criticidad_actual.name else None,
                        f"Criticidad actualizada: {nueva_criticidad_id}" if str(nueva_criticidad_id) != str(criticidad_id_actual) else None
                    ]
                }, status=200)

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)