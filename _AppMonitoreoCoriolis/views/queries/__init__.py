# Queries - Views que solo consultan datos
from .DatosHistoricosFlujoQuery import DatosHistoricosFlujoQueryView
from .DatosHistoricosPresionQuery import DatosHistoricosPresionQueryView
from .DatosHistoricosTemperaturaQuery import DatosHistoricosTemperaturaQueryView
from .DatosTiempoRealQuery import DatosTiempoRealQueryView
from .DatosTendenciasQuery import DatosTendenciasQueryView
from .DetalleBatchQuery import DetalleBatchQueryView

__all__ = [
    'DatosHistoricosFlujoQueryView',
    'DatosHistoricosPresionQueryView',
    'DatosHistoricosTemperaturaQueryView',
    'DatosTiempoRealQueryView',
    'DatosTendenciasQueryView',
    'DetalleBatchQueryView'
]
