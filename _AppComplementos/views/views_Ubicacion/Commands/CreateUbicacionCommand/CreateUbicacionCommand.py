from rest_framework.permissions import IsAuthenticated
from repoGenerico.views_base import BaseCreateView
from rest_framework.response import Response
from rest_framework import status
from _AppAdmin.mixins import ComplementosPermissionMixin

from .....models import Ubicacion
from .....serializers import UbicacionSerializer

from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    post=extend_schema(tags=['Ubicación']),
)

# 🔹 Crear
class CreateUbicacionView(ComplementosPermissionMixin, BaseCreateView):
    model = Ubicacion
    serializer_class = UbicacionSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            obj = serializer.save()
            return Response({
                "success": True,
                "message": "Ubicación creada exitosamente",
                "id": obj.id
            }, status=status.HTTP_201_CREATED)
        
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
