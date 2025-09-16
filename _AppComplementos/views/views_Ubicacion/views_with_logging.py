"""
Vistas para Ubicacion con logging automatico de acciones
"""
from _AppAdmin.mixins import UniversalActionLogMixin
from _AppComplementos.models import Ubicacion
from .Commands.CreateUbicacionCommand.CreateUbicacionCommand import CreateUbicacionView
from .Commands.UpdateUbicacionCommand.UpdateUbicacionCommand import UpdateUbicacionView
from .Commands.DeleteUbicacionCommand.DeleteUbicacionCommand import DeleteUbicacionView


class CreateUbicacionWithLogging(UniversalActionLogMixin, CreateUbicacionView):
    log_config = {
        'affected_type': 'ubicacion',
        'get_value': lambda obj: obj.nombre,
        'model_class': Ubicacion,
    }


class UpdateUbicacionWithLogging(UniversalActionLogMixin, UpdateUbicacionView):
    log_config = {
        'affected_type': 'ubicacion',
        'get_value': lambda obj: obj.nombre,
        'model_class': Ubicacion,
    }


class DeleteUbicacionWithLogging(UniversalActionLogMixin, DeleteUbicacionView):
    log_config = {
        'affected_type': 'ubicacion',
        'get_value': lambda obj: obj.nombre,
        'model_class': Ubicacion,
    }