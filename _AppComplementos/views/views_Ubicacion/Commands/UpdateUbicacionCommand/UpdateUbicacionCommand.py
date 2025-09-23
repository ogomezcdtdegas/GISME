from rest_framework.permissions import IsAuthenticated
from repoGenerico.views_base import BaseRetrieveUpdateView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .....models import Ubicacion
from .....serializers import UbicacionSerializer


from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    put=extend_schema(tags=['Ubicación']),
    patch=extend_schema(tags=['Ubicación']),
)

# 🔹 Actualizar
class UpdateUbicacionView(BaseRetrieveUpdateView):
    model = Ubicacion
    serializer_class = UbicacionSerializer
    permission_classes = [IsAuthenticated]
    
    def put(self, request, **kwargs):
        try:
            # Extraer el ID del objeto usando nombres de parámetros comunes
            obj_id = self._get_object_id_from_kwargs(kwargs)
            
            obj = get_object_or_404(self.model, id=obj_id)
            serializer = self.serializer_class(obj, data=request.data, partial=True)

            if serializer.is_valid():
                instance = serializer.save()
                return Response({"success": True, "message": "Actualización exitosa"}, status=status.HTTP_200_OK)
            
            # Mostrar solo el primer error encontrado en español
            error_message = "Error de validación"
            if 'nombre' in serializer.errors:
                error_message = serializer.errors['nombre'][0]
            elif 'latitud' in serializer.errors:
                error_message = serializer.errors['latitud'][0]
            elif 'longitud' in serializer.errors:
                error_message = serializer.errors['longitud'][0]
            elif 'non_field_errors' in serializer.errors:
                error_message = serializer.errors['non_field_errors'][0]
            else:
                # Para otros campos, mostrar el primer error encontrado
                for field, errors in serializer.errors.items():
                    if errors:
                        error_message = f"{field}: {errors[0]}"
                        break
            
            return Response({"success": False, "error": error_message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def perform_update(self, serializer):
        """Override para agregar logging después de la actualización"""
        # Esta función ya no se necesita porque el logging se maneja en put()
        pass
