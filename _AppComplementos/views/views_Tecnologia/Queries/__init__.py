
# Only import TecnologiaPaginatedAPI from GetAllTecnologiaPagQuery
from .GetAllTecnologiaPagQuery.GetAllTecnologiaPagQuery import TecnologiaPaginatedAPI
# Import TecnologiaPaginatedHTML from views_template
from ..views_template import TecnologiaPaginatedHTML

# For modular import compatibility in urls.py
import sys as _sys
import importlib as _importlib
_GetAllTecnologiaPagQuery = _importlib.import_module('.GetAllTecnologiaPagQuery', __package__)
_sys.modules[__name__ + '.GetAllTecnologiaPagQuery'] = _GetAllTecnologiaPagQuery
