from repoGenerico.views_base import BaseListView
from _AppComplementos.models import Ubicacion
from _AppComplementos.serializers import UbicacionSerializer
from _AppAuth.utils import get_user_role_context
from _AppAdmin.mixins import ComplementosPermissionMixin

class UbicacionListPagHTML(ComplementosPermissionMixin, BaseListView):
    model = Ubicacion
    serializer_class = UbicacionSerializer
    template_name = "_AppComplementos/templates_ubicacion/index.html"
    active_section = "complementos_ubicacion"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Agregar contexto de permisos de usuario
        if hasattr(self.request, 'user'):
            context.update(get_user_role_context(self.request.user))
        
        return context

    def get_allowed_ordering_fields(self):
        return ['created_at', 'nombre', 'latitud', 'longitud']

    def get_search_fields(self):
        return ['nombre']
