from repoGenerico.views_base import BaseRetrieveUpdateView, BaseReadForIdView
from .....models import TipoCriticidadCriticidad
from .....serializers import TipoCriticidadCriticidadSerializer
from django.http import JsonResponse
from rest_framework import status

class editarTipCriticidad(BaseRetrieveUpdateView, BaseReadForIdView):  
    model = TipoCriticidadCriticidad
    serializer_class = TipoCriticidadCriticidadSerializer

    def put(self, request, *args, **kwargs):
        relacion_id = kwargs.get("obj_id")
        data = request.data

        if not relacion_id:
            return JsonResponse({'success': False, 'error': 'El ID de la relación es obligatorio'}, status=status.HTTP_400_BAD_REQUEST)

        tipo_criticidad_id = data.get('tipo_criticidad_id')
        criticidad_id = data.get('criticidad_id')

        try:
            relacion = self.get_object_by_id(TipoCriticidadCriticidad, relacion_id, "La relación no existe")
            cambios = []

            # Verificar y actualizar los valores si han cambiado
            if tipo_criticidad_id and str(relacion.tipo_criticidad_id) != str(tipo_criticidad_id):
                relacion.tipo_criticidad_id = tipo_criticidad_id
                cambios.append(f"Nuevo TipoCriticidadID: {tipo_criticidad_id}")

            if criticidad_id and str(relacion.criticidad_id) != str(criticidad_id):
                relacion.criticidad_id = criticidad_id
                cambios.append(f"Nuevo CriticidadID: {criticidad_id}")

            # Guardar cambios si existen
            if cambios:
                relacion.save()
                return JsonResponse({"success": True, "message": "Relación actualizada correctamente", "cambios": cambios}, status=status.HTTP_200_OK)
            else:
                return JsonResponse({"success": False, "message": "No hay cambios para actualizar"}, status=status.HTTP_400_BAD_REQUEST)
        
        except ValueError as e:
            return JsonResponse({"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
