# __init__.py para views_Sistema

# Importar Commands
from .Commands import (
    CrearSistemaCommandView,
    EditarSistemaCommandView,
    EliminarSistemaCommandView
)

# Importar Queries
from .Queries import (
    ListarSistemasQueryView,
    ListarTodosSistemasQueryView,
    ObtenerSistemaQueryView
)

# Importar Templates
from .views_templates import SistemasIndexView, SistemaBaseView

__all__ = [
    # Commands
    'CrearSistemaCommandView',
    'EditarSistemaCommandView', 
    'EliminarSistemaCommandView',
    
    # Queries
    'ListarSistemasQueryView',
    'ListarTodosSistemasQueryView',
    'ObtenerSistemaQueryView',
    
    # Templates & Debug
    'SistemasIndexView',
    'SistemaBaseView'
]
