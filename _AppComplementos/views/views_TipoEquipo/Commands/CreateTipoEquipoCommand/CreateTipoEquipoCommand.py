from repoGenerico.views_base import BaseCreateView, BaseReadForIdView
from _AppComplementos.models import TipoEquipo, ProductoTipoCritCrit, TipoEquipoProducto
from _AppComplementos.serializers import TipoEquipoProductoSerializer
from django.http import JsonResponse
from rest_framework import status

# 🔹 Creación independiente
class crearTipoEquipo(BaseCreateView, BaseReadForIdView):
    model = TipoEquipoProducto
    serializer_class = TipoEquipoProductoSerializer

    def post(self, request):
        data = request.data
        tipo_equipo_name = data.get('name')
        producto_id = data.get('producto_id')
        tipo_criticidad_id = data.get('tipo_criticidad_id')
        criticidad_id = data.get('criticidad_id')

        if not all([tipo_equipo_name, producto_id, tipo_criticidad_id, criticidad_id]):
            return JsonResponse({'success': False, 'error': 'Todos los campos son obligatorios'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Buscar la relación ProductoTipoCritCrit basándose en los IDs
            producto_relacion = ProductoTipoCritCrit.objects.filter(
                producto_id=producto_id,
                relacion_tipo_criticidad__tipo_criticidad_id=tipo_criticidad_id,
                relacion_tipo_criticidad__criticidad_id=criticidad_id
            ).first()

            if not producto_relacion:
                return JsonResponse({'success': False, 'error': 'La combinación de producto, tipo de criticidad y criticidad no existe'}, status=status.HTTP_400_BAD_REQUEST)

            tipo_equipo, _ = self.get_or_create_object(TipoEquipo, name=tipo_equipo_name)

            relacion, created = self.get_or_create_object(
                TipoEquipoProducto,
                tipo_equipo=tipo_equipo,
                relacion_producto=producto_relacion
            )

            if not created:
                return JsonResponse({"success": False, "message": "Esta relación ya existe"}, status=status.HTTP_200_OK)

            return JsonResponse({"success": True, "message": "Registro exitoso", "data": TipoEquipoProductoSerializer(relacion).data}, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return JsonResponse({"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
