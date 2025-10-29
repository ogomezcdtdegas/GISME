# Queries - Views que solo consultan datos
from .DatosHistoricosFlujoQuery import DatosHistoricosFlujoQueryView
from .DatosHistoricosPresionQuery import DatosHistoricosPresionQueryView
from .DatosHistoricosTemperaturaQuery import DatosHistoricosTemperaturaQueryView
from .DatosTiempoRealQuery import DatosTiempoRealQueryView
from .DatosTendenciasQuery import DatosTendenciasQueryView
from .DetalleBatchQuery import DetalleBatchQueryView
from .ListarBatchesQuery import ListarBatchesQueryView
from .ListarTicketsQuery import ListarTicketsQueryView

__all__ = [
    'DatosHistoricosFlujoQueryView',
    'DatosHistoricosPresionQueryView',
    'DatosHistoricosTemperaturaQueryView',
    'DatosTiempoRealQueryView',
    'DatosTendenciasQueryView',
    'DetalleBatchQueryView',
    'ListarBatchesQueryView',
    'ListarTicketsQueryView'
]
