from repoGenerico.views_base import BaseCreateView, BaseReadForIdView
from .....models import TipoCriticidad, Criticidad, TipoCriticidadCriticidad
from .....serializers import TipoCriticidadCriticidadSerializer
from django.http import JsonResponse
from rest_framework import status

from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    post=extend_schema(tags=['TipoCriticidad']),
)

# 🔹 Creación independiente
class crearTipCriticidad(BaseCreateView, BaseReadForIdView):
    model = TipoCriticidadCriticidad
    serializer_class = TipoCriticidadCriticidadSerializer

    def post(self, request):
        data = request.data
        tipo_criticidad_name = data.get('name')
        criticidad_id = data.get('criticidad_id')

        if not criticidad_id:
            return JsonResponse({'success': False, 'error': 'El campo criticidad_id es obligatorio'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            tipo_criticidad, _ = self.get_or_create_object(TipoCriticidad, name=tipo_criticidad_name)
            criticidad = self.get_object_by_id(Criticidad, criticidad_id, "La criticidad no existe")

            relacion, created = self.get_or_create_object(
                TipoCriticidadCriticidad,
                tipo_criticidad=tipo_criticidad,
                criticidad=criticidad
            )

            if not created:
                return JsonResponse({"success": False, "message": "Esta relación ya existe"}, status=status.HTTP_200_OK)

            return JsonResponse({"success": True, "message": "Registro exitoso", "data": TipoCriticidadCriticidadSerializer(relacion).data}, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return JsonResponse({"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)