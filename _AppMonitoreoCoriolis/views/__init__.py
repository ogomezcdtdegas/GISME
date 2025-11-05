# Vistas modularizadas para Monitoreo Coriolis
# Estructura CQS (Command Query Separation)

# Template Views
from .templates import MonitoreoCoriolisBaseView, MonitoreoCoriolisSistemaView

# Query Views (solo consultan datos)
from .queries import (
    DatosHistoricosFlujoQueryView,
    DatosHistoricosPresionQueryView,
    DatosHistoricosTemperaturaQueryView,
    DatosTiempoRealQueryView,
    DatosTendenciasQueryView,
    DetalleBatchQueryView,
    ListarBatchesQueryView,
    ListarTicketsQueryView
)

# Command Views (modifican datos)
from .commands import DetectarBatchesCommandView, AsignarTicketBatchCommandView

# Mantener nombres originales para compatibilidad
DatosHistoricosFlujoView = DatosHistoricosFlujoQueryView
DatosHistoricosPresionView = DatosHistoricosPresionQueryView
DatosHistoricosTemperaturaView = DatosHistoricosTemperaturaQueryView
DatosTiempoRealView = DatosTiempoRealQueryView
DatosTendenciasView = DatosTendenciasQueryView
DetectarBatchesView = DetectarBatchesCommandView
DetalleBatchView = DetalleBatchQueryView
ListarBatchesView = ListarBatchesQueryView
AsignarTicketBatchView = AsignarTicketBatchCommandView

__all__ = [
    # Template Views
    'MonitoreoCoriolisBaseView',
    'MonitoreoCoriolisSistemaView',
    
    # Query Views (new names)
    'DatosHistoricosFlujoQueryView',
    'DatosHistoricosPresionQueryView',
    'DatosHistoricosTemperaturaQueryView',
    'DatosTiempoRealQueryView',
    'DatosTendenciasQueryView',
    'DetalleBatchQueryView',
    'ListarBatchesQueryView',
    'ListarTicketsQueryView',
    
    # Command Views (new names)
    'DetectarBatchesCommandView',
    'AsignarTicketBatchCommandView',
    
    # Legacy names for compatibility
    'DatosHistoricosFlujoView',
    'DatosHistoricosPresionView',
    'DatosHistoricosTemperaturaView',
    'DatosTiempoRealView',
    'DatosTendenciasView',
    'DetectarBatchesView',
    'DetalleBatchView',
    'ListarBatchesView',
    'AsignarTicketBatchView'
]
