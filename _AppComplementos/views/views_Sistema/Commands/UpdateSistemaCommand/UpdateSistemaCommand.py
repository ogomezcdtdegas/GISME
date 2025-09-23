from rest_framework.permissions import IsAuthenticated
from repoGenerico.views_base import BaseRetrieveUpdateView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .....models import Sistema
from .....serializers import SistemaSerializer


from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    put=extend_schema(tags=['Sistema']),
    patch=extend_schema(tags=['Sistema']),
)

class EditarSistemaCommandView(BaseRetrieveUpdateView):
    """CBV Command para editar un sistema existente usando BaseRetrieveUpdateView"""
    model = Sistema
    serializer_class = SistemaSerializer
    permission_classes = [IsAuthenticated]
    
    def put(self, request, **kwargs):
        try:
            # Extraer el ID del objeto usando nombres de parámetros comunes
            obj_id = self._get_object_id_from_kwargs(kwargs)
            print(f"🔍 Intentando actualizar ID: {obj_id}")  # Verificar el ID en consola
            print(f"📥 Datos recibidos: {request.data}")  # Ver los datos que llegan
            
            obj = get_object_or_404(self.model, id=obj_id)
            serializer = self.serializer_class(obj, data=request.data, partial=True)

            if serializer.is_valid():
                instance = serializer.save()
                print(f"✅ Actualización exitosa para ID: {obj_id}")
                return Response({"success": True, "message": "Actualización exitosa"}, status=status.HTTP_200_OK)
            
            print(f"❌ Errores de validación: {serializer.errors}")
            # Mostrar solo el primer error encontrado en español
            error_message = "Error de validación"
            if 'tag' in serializer.errors:
                error_message = serializer.errors['tag'][0]
            elif 'sistema_id' in serializer.errors:
                error_message = serializer.errors['sistema_id'][0]
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
