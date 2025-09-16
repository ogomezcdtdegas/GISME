from repoGenerico.views_base import BaseRetrieveUpdateView
from .....models import Ubicacion
from .....serializers import UbicacionSerializer
from _AppAdmin.models import UserActionLog
from django.utils import timezone

from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    put=extend_schema(tags=['Ubicación']),
    patch=extend_schema(tags=['Ubicación']),
)


# 🔹 Actualizar
class UpdateUbicacionView(BaseRetrieveUpdateView):
    model = Ubicacion
    serializer_class = UbicacionSerializer
    
    def perform_update(self, serializer):
        """Override para agregar logging después de la actualización"""
        # Guardar la instancia actualizada
        instance = serializer.save()
        
        # Registrar la acción en el log
        UserActionLog.objects.create(
            user=self.request.user,
            email=self.request.user.email,
            action='editar',
            action_datetime=timezone.now(),
            affected_type='ubicacion',
            affected_value=instance.nombre,  # Usar el valor actualizado
            affected_id=instance.id,
            ip_address=self.request.META.get('REMOTE_ADDR', '')
        )
