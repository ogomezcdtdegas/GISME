"""
Vistas para Sistema con logging automatico de acciones
"""
from _AppAdmin.mixins import UniversalActionLogMixin
from _AppComplementos.models import Sistema
from .Commands.CreateSistemaCommand.CreateSistemaCommand import CrearSistemaCommandView
from .Commands.UpdateSistemaCommand.UpdateSistemaCommand import EditarSistemaCommandView
from .Commands.DeleteSistemaCommand.DeleteSistemaCommand import EliminarSistemaCommandView


class CreateSistemaWithLogging(UniversalActionLogMixin, CrearSistemaCommandView):
    log_config = {
        'affected_type': 'sistema',
        'get_value': lambda obj: f"{obj.tag} - {obj.sistema_id}",
        'model_class': Sistema,
    }


class UpdateSistemaWithLogging(UniversalActionLogMixin, EditarSistemaCommandView):
    log_config = {
        'affected_type': 'sistema',
        'get_value': lambda obj: f"{obj.tag} - {obj.sistema_id}",
        'model_class': Sistema,
    }


class DeleteSistemaWithLogging(UniversalActionLogMixin, EliminarSistemaCommandView):
    log_config = {
        'affected_type': 'sistema',
        'get_value': lambda obj: f"{obj.tag} - {obj.sistema_id}",
        'model_class': Sistema,
    }