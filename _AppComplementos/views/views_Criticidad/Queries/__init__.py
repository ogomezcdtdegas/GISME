from .GetAllCriticidadPagQuery import CriticidadPaginatedAPI, CriticidadPaginatedHTML

# For modular import compatibility in urls.py
import sys as _sys
import importlib as _importlib
_GetAllCriticidadPagQuery = _importlib.import_module('.GetAllCriticidadPagQuery', __package__)
_sys.modules[__name__ + '.GetAllCriticidadPagQuery'] = _GetAllCriticidadPagQuery
from .GetAllCriticidadListQuery import GetAllCriticidadListQuery
from .GetCriticidadPorTipoCritQuery import GetCriticidadPorTipoCritQuery