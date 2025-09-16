from rest_framework.permissions import IsAuthenticated
from repoGenerico.views_base import BaseRetrieveUpdateView

from .....models import Sistema
from .....serializers import SistemaSerializer
from _AppAdmin.models import UserActionLog
from django.utils import timezone

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
            affected_type='sistema',
            affected_value=f"{instance.tag} - {instance.sistema_id}",  # Usar los valores actualizados
            affected_id=instance.id,
            ip_address=self.request.META.get('REMOTE_ADDR', '')
        )
