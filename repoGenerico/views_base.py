from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

''' XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX '''
''' ---------------------------------------------------------- Querys -------------------------------------------------------------------------------------- '''
''' -------------------------------------------------------------------------------------------------------------------------------------------------------- '''

class BaseReadForIdView(APIView):
    model = None  # Se define en la subclase
    serializer_class = None

    @staticmethod
    def get_object_by_id(model_class, obj_id, error_message):
        """ Obtiene un objeto por ID o lanza un error si no existe """
        try:
            return model_class.objects.get(id=obj_id)
        except model_class.DoesNotExist:
            raise ValueError(error_message)

    @staticmethod
    def get_or_create_object(model_class, **kwargs):
        """ Obtiene o crea un objeto basado en los argumentos """
        return model_class.objects.get_or_create(**kwargs)

    def get(self, request, obj_id):
        """ Vista GET para obtener un objeto por su ID """
        try:
            obj = self.get_object_by_id(self.model, obj_id, "Objeto no encontrado")
            serializer = self.serializer_class(obj)
            return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

''' -------------------------------------------------------------------------------------------------------------------------------------------------------- '''

class BaseListView(APIView):


    model = None  # Se define en la subclase
    serializer_class = None
    template_name = None  # Para renderizado en HTML (solo si se usa)
    active_section = None
    default_per_page = 10
    default_ordering = 'created_at'

    def get_queryset(self):
        """Subclases pueden sobrescribir para optimizar el queryset (select_related, annotate, etc)."""
        return self.model.objects.all()

    def get_allowed_ordering_fields(self):
        """Campos permitidos para ordenamiento. Override en subclases."""
        return ['created_at', 'name']

    def get_search_fields(self):
        """Campos permitidos para búsqueda. Override en subclases."""
        return []

    def get_default_ordering(self):
        """Ordenamiento por defecto. Override en subclases si es necesario."""
        return getattr(self, 'default_ordering', 'created_at')

    def apply_search_filters(self, queryset, search_query):
        fields = self.get_search_fields()
        if fields and search_query:
            from django.db.models import Q
            q = Q()
            for field in fields:
                q |= Q(**{f"{field}__icontains": search_query})
            queryset = queryset.filter(q)
        return queryset

    def paginate_queryset(self, queryset, per_page, page_number):
        paginator = Paginator(queryset, per_page)
        return paginator.get_page(page_number)

    def get_paginated_response(self, page_obj, search_query=None):
        data = self.serializer_class(page_obj, many=True).data
        return Response({
            "results": data,
            "has_previous": page_obj.has_previous(),
            "has_next": page_obj.has_next(),
            "previous_page_number": page_obj.previous_page_number() if page_obj.has_previous() else None,
            "next_page_number": page_obj.next_page_number() if page_obj.has_next() else None,
            "current_page": page_obj.number,
            "total_pages": page_obj.paginator.num_pages,
            "total_count": page_obj.paginator.count,
            "search_query": search_query,
        }, status=status.HTTP_200_OK)

    def get(self, request):
        request.GET = request.GET.copy()
        if 'per_page' not in request.GET:
            request.GET['per_page'] = str(self.default_per_page)
        if 'ordering' not in request.GET:
            request.GET['ordering'] = self.get_default_ordering()

        ordering = request.GET.get('ordering', self.get_default_ordering())
        allowed_fields = self.get_allowed_ordering_fields()
        if ordering.lstrip('-') not in allowed_fields:
            ordering = self.get_default_ordering()

        queryset = self.get_queryset()
        search_query = request.GET.get('search', '').strip()
        if search_query:
            queryset = self.apply_search_filters(queryset, search_query)
        queryset = queryset.order_by(ordering)

        per_page = int(request.GET.get('per_page', self.default_per_page))
        page_number = int(request.GET.get('page', 1))
        page_obj = self.paginate_queryset(queryset, per_page, page_number)

        # Si es petición AJAX, responde JSON paginado; si no, renderiza template si está definido
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or not self.template_name:
            return self.get_paginated_response(page_obj, search_query)
        return render(request, self.template_name, {"objects": page_obj, **self.get_context_data()})

    def get_context_data(self, **kwargs):
        context = kwargs.copy() if kwargs else {}
        if self.active_section:
            context["active_section"] = self.active_section
        return context

''' XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX '''


''' XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX '''
''' --------------------------------------------------------------------- Commands ------------------------------------------------------------------------- '''
''' -------------------------------------------------------------------------------------------------------------------------------------------------------- '''
class BaseCreateView(APIView):
    model = None
    serializer_class = None
    http_method_names = ['post']  # <-- Solo permite POST

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            obj = serializer.save()
            return Response({
                "success": True,
                "message": "Registro exitoso",
                "id": obj.id
            }, status=status.HTTP_201_CREATED)
        
        return Response({"success": False, "error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

''' -------------------------------------------------------------------------------------------------------------------------------------------------------- '''
class BaseRetrieveUpdateView(APIView):
    model = None
    serializer_class = None

    def get(self, request, **kwargs):
        """Vista GET para obtener un objeto por su ID"""
        try:
            # Extraer el ID del objeto usando nombres de parámetros comunes
            obj_id = self._get_object_id_from_kwargs(kwargs)
            print(f"🔍 Obteniendo objeto ID: {obj_id}")
            
            obj = get_object_or_404(self.model, id=obj_id)
            serializer = self.serializer_class(obj)
            return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, **kwargs):
        try:
            # Extraer el ID del objeto usando nombres de parámetros comunes
            obj_id = self._get_object_id_from_kwargs(kwargs)
            print(f"🔍 Intentando actualizar ID: {obj_id}")  # Verificar el ID en consola
            print(f"📥 Datos recibidos: {request.data}")  # Ver los datos que llegan
            
            obj = get_object_or_404(self.model, id=obj_id)
            serializer = self.serializer_class(obj, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                print(f"✅ Actualización exitosa para ID: {obj_id}")
                return Response({"success": True, "message": "Actualización exitosa"}, status=status.HTTP_200_OK)
            
            print(f"❌ Errores de validación: {serializer.errors}")
            return Response({"success": False, "error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def _get_object_id_from_kwargs(self, kwargs):
        """Extrae el ID del objeto de los kwargs usando nombres de parámetros comunes"""
        common_id_params = ['obj_id', 'pk', 'id', 'sistema_id', 'equipo_id', 'ubicacion_id']
        for param in common_id_params:
            if param in kwargs:
                return kwargs[param]
        raise ValueError("No se encontró un parámetro de ID válido en la URL")

''' -------------------------------------------------------------------------------------------------------------------------------------------------------- '''
class BaseDeleteView(APIView):
    model = None
    permission_classes = []
    http_method_names = ['delete']  # Solo permite DELETE

    def delete(self, request, **kwargs):
        """Vista DELETE para eliminar un objeto por su ID"""
        try:
            # Extraer el ID del objeto usando nombres de parámetros comunes
            obj_id = self._get_object_id_from_kwargs(kwargs)
            
            obj = get_object_or_404(self.model, id=obj_id)
            obj_info = self.get_object_info(obj)
            obj.delete()
            
            return Response({
                "success": True,
                "message": f"Registro {obj_info} eliminado exitosamente"
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False,
                "error": f"Error al eliminar registro: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get_object_info(self, obj):
        """Obtiene información descriptiva del objeto para el mensaje de confirmación"""
        # Por defecto usa __str__, las subclases pueden sobrescribir este método
        return str(obj)
    
    def _get_object_id_from_kwargs(self, kwargs):
        """Extrae el ID del objeto de los kwargs usando nombres de parámetros comunes"""
        common_id_params = ['obj_id', 'pk', 'id', 'sistema_id', 'equipo_id', 'ubicacion_id']
        for param in common_id_params:
            if param in kwargs:
                return kwargs[param]
        raise ValueError("No se encontró un parámetro de ID válido en la URL")

''' -------------------------------------------------------------------------------------------------------------------------------------------------------- '''
class BaseRetrieveView(APIView):
    """Vista base para obtener un objeto específico por ID"""
    model = None
    serializer_class = None
    permission_classes = []

    def get(self, request, **kwargs):
        """Obtiene un objeto específico por su ID"""
        try:
            # Extraer el ID del objeto usando nombres de parámetros comunes
            obj_id = self._get_object_id_from_kwargs(kwargs)
            
            # Si el modelo tiene select_related definido, aplicarlo
            queryset = self.get_queryset()
            obj = get_object_or_404(queryset, id=obj_id)
            serializer = self.serializer_class(obj)
            return Response({
                "success": True,
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False,
                "error": f"Error al obtener registro: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get_queryset(self):
        """Queryset base, las subclases pueden sobrescribir para añadir select_related, etc."""
        return self.model.objects.all()
    
    def _get_object_id_from_kwargs(self, kwargs):
        """Extrae el ID del objeto de los kwargs usando nombres de parámetros comunes"""
        common_id_params = ['obj_id', 'pk', 'id', 'sistema_id', 'equipo_id', 'ubicacion_id']
        for param in common_id_params:
            if param in kwargs:
                return kwargs[param]
        raise ValueError("No se encontró un parámetro de ID válido en la URL")

''' -------------------------------------------------------------------------------------------------------------------------------------------------------- '''
class BaseListQueryView(APIView):
    """Vista base para listar objetos con paginación y búsqueda - optimizada para APIs"""
    model = None
    serializer_class = None
    permission_classes = []

    def get(self, request):
        """Lista objetos con paginación y búsqueda"""
        try:
            # Parámetros de paginación
            page = int(request.GET.get('page', 1))
            per_page = int(request.GET.get('per_page', 10))
            
            # Parámetros de búsqueda y ordenamiento
            search = request.GET.get('search', '').strip()
            ordering = request.GET.get('ordering', self.get_default_ordering())
            
            # Validar campo de ordenamiento
            if ordering not in self.get_allowed_ordering_fields():
                ordering = self.get_default_ordering()
            
            # Construir queryset base optimizado
            queryset = self.get_queryset()
            
            # Aplicar filtros de búsqueda
            if search:
                queryset = self.apply_search_filters(queryset, search)
            
            # Aplicar ordenamiento
            queryset = queryset.order_by(ordering)
            
            # Paginar resultados
            paginator = Paginator(queryset, per_page)
            page_obj = paginator.get_page(page)
            
            # Serializar datos
            serializer = self.serializer_class(page_obj.object_list, many=True)
            
            return Response({
                'results': serializer.data,
                'has_previous': page_obj.has_previous(),
                'has_next': page_obj.has_next(),
                'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
                'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_count': paginator.count,
                'search_query': search
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': f'Error al obtener registros: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get_queryset(self):
        """Queryset base, las subclases pueden sobrescribir para añadir select_related, etc."""
        return self.model.objects.all()
    
    def get_default_ordering(self):
        """Ordenamiento por defecto"""
        return 'id'
    
    def get_allowed_ordering_fields(self):
        """Campos permitidos para ordenamiento"""
        return ['id', '-id']
    
    def apply_search_filters(self, queryset, search_query):
        """Aplica filtros de búsqueda al queryset. Override en subclases para búsqueda personalizada."""
        return queryset

''' XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX '''
''' --------------------------------------------------------------------- Commands ------------------------------------------------------------------------- '''
''' -------------------------------------------------------------------------------------------------------------------------------------------------------- '''
class BaseCreateView(APIView):
    model = None
    serializer_class = None
    http_method_names = ['post']  # <-- Solo permite POST

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            obj = serializer.save()
            return Response({
                "success": True,
                "message": "Registro exitoso",
                "id": obj.id
            }, status=status.HTTP_201_CREATED)
        
        return Response({"success": False, "error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

''' -------------------------------------------------------------------------------------------------------------------------------------------------------- '''
class BaseRetrieveUpdateView(APIView):
    model = None
    serializer_class = None

    def get(self, request, **kwargs):
        """Vista GET para obtener un objeto por su ID"""
        try:
            # Extraer el ID del objeto usando nombres de parámetros comunes
            obj_id = self._get_object_id_from_kwargs(kwargs)
            print(f"🔍 Obteniendo objeto ID: {obj_id}")
            
            obj = get_object_or_404(self.model, id=obj_id)
            serializer = self.serializer_class(obj)
            return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, **kwargs):
        try:
            # Extraer el ID del objeto usando nombres de parámetros comunes
            obj_id = self._get_object_id_from_kwargs(kwargs)
            print(f"🔍 Intentando actualizar ID: {obj_id}")  # Verificar el ID en consola
            print(f"📥 Datos recibidos: {request.data}")  # Ver los datos que llegan
            
            obj = get_object_or_404(self.model, id=obj_id)
            serializer = self.serializer_class(obj, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                print(f"✅ Actualización exitosa para ID: {obj_id}")
                return Response({"success": True, "message": "Actualización exitosa"}, status=status.HTTP_200_OK)
            
            print(f"❌ Errores de validación: {serializer.errors}")
            return Response({"success": False, "error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def _get_object_id_from_kwargs(self, kwargs):
        """Extrae el ID del objeto de los kwargs usando nombres de parámetros comunes"""
        common_id_params = ['obj_id', 'pk', 'id', 'sistema_id', 'equipo_id', 'ubicacion_id']
        for param in common_id_params:
            if param in kwargs:
                return kwargs[param]
        raise ValueError("No se encontró un parámetro de ID válido en la URL")

''' -------------------------------------------------------------------------------------------------------------------------------------------------------- '''
class BaseDeleteView(APIView):
    model = None
    permission_classes = []
    http_method_names = ['delete']  # Solo permite DELETE

    def delete(self, request, **kwargs):
        """Vista DELETE para eliminar un objeto por su ID"""
        try:
            # Extraer el ID del objeto usando nombres de parámetros comunes
            obj_id = self._get_object_id_from_kwargs(kwargs)
            
            obj = get_object_or_404(self.model, id=obj_id)
            obj_info = self.get_object_info(obj)
            obj.delete()
            
            return Response({
                "success": True,
                "message": f"Registro {obj_info} eliminado exitosamente"
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False,
                "error": f"Error al eliminar registro: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get_object_info(self, obj):
        """Obtiene información descriptiva del objeto para el mensaje de confirmación"""
        # Por defecto usa __str__, las subclases pueden sobrescribir este método
        return str(obj)
    
    def _get_object_id_from_kwargs(self, kwargs):
        """Extrae el ID del objeto de los kwargs usando nombres de parámetros comunes"""
        common_id_params = ['obj_id', 'pk', 'id', 'sistema_id', 'equipo_id', 'ubicacion_id']
        for param in common_id_params:
            if param in kwargs:
                return kwargs[param]
        raise ValueError("No se encontró un parámetro de ID válido en la URL")

''' -------------------------------------------------------------------------------------------------------------------------------------------------------- '''
class BaseRetrieveView(APIView):
    """Vista base para obtener un objeto específico por ID"""
    model = None
    serializer_class = None
    permission_classes = []

    def get(self, request, **kwargs):
        """Obtiene un objeto específico por su ID"""
        try:
            # Extraer el ID del objeto usando nombres de parámetros comunes
            obj_id = self._get_object_id_from_kwargs(kwargs)
            
            # Si el modelo tiene select_related definido, aplicarlo
            queryset = self.get_queryset()
            obj = get_object_or_404(queryset, id=obj_id)
            serializer = self.serializer_class(obj)
            return Response({
                "success": True,
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False,
                "error": f"Error al obtener registro: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get_queryset(self):
        """Queryset base, las subclases pueden sobrescribir para añadir select_related, etc."""
        return self.model.objects.all()
    
    def _get_object_id_from_kwargs(self, kwargs):
        """Extrae el ID del objeto de los kwargs usando nombres de parámetros comunes"""
        common_id_params = ['obj_id', 'pk', 'id', 'sistema_id', 'equipo_id', 'ubicacion_id']
        for param in common_id_params:
            if param in kwargs:
                return kwargs[param]
        raise ValueError("No se encontró un parámetro de ID válido en la URL")

''' -------------------------------------------------------------------------------------------------------------------------------------------------------- '''
class BaseListQueryView(APIView):
    """Vista base para listar objetos con paginación y búsqueda - optimizada para APIs"""
    model = None
    serializer_class = None
    permission_classes = []

    def get(self, request):
        """Lista objetos con paginación y búsqueda"""
        try:
            # Parámetros de paginación
            page = int(request.GET.get('page', 1))
            per_page = int(request.GET.get('per_page', 10))
            
            # Parámetros de búsqueda y ordenamiento
            search = request.GET.get('search', '').strip()
            ordering = request.GET.get('ordering', self.get_default_ordering())
            
            # Validar campo de ordenamiento
            if ordering not in self.get_allowed_ordering_fields():
                ordering = self.get_default_ordering()
            
            # Construir queryset base optimizado
            queryset = self.get_queryset()
            
            # Aplicar filtros de búsqueda
            if search:
                queryset = self.apply_search_filters(queryset, search)
            
            # Aplicar ordenamiento
            queryset = queryset.order_by(ordering)
            
            # Paginar resultados
            paginator = Paginator(queryset, per_page)
            page_obj = paginator.get_page(page)
            
            # Serializar datos
            serializer = self.serializer_class(page_obj.object_list, many=True)
            
            return Response({
                'results': serializer.data,
                'has_previous': page_obj.has_previous(),
                'has_next': page_obj.has_next(),
                'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
                'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_count': paginator.count,
                'search_query': search
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': f'Error al obtener registros: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get_queryset(self):
        """Queryset base, las subclases pueden sobrescribir para añadir select_related, etc."""
        return self.model.objects.all()
    
    def get_default_ordering(self):
        """Ordenamiento por defecto"""
        return 'id'
    
    def get_allowed_ordering_fields(self):
        """Campos permitidos para ordenamiento"""
        return ['id', '-id']
    
    def apply_search_filters(self, queryset, search_query):
        """Aplica filtros de búsqueda al queryset. Override en subclases para búsqueda personalizada."""
        return queryset

''' XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX '''
''' --------------------------------------------------------------------- Commands ------------------------------------------------------------------------- '''
''' -------------------------------------------------------------------------------------------------------------------------------------------------------- '''
class BaseCreateView(APIView):
    model = None
    serializer_class = None
    http_method_names = ['post']  # <-- Solo permite POST

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            obj = serializer.save()
            return Response({
                "success": True,
                "message": "Registro exitoso",
                "id": obj.id
            }, status=status.HTTP_201_CREATED)
        
        return Response({"success": False, "error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

''' -------------------------------------------------------------------------------------------------------------------------------------------------------- '''
class BaseRetrieveUpdateView(APIView):
    model = None
    serializer_class = None

    def get(self, request, **kwargs):
        """Vista GET para obtener un objeto por su ID"""
        try:
            # Extraer el ID del objeto usando nombres de parámetros comunes
            obj_id = self._get_object_id_from_kwargs(kwargs)
            print(f"🔍 Obteniendo objeto ID: {obj_id}")
            
            obj = get_object_or_404(self.model, id=obj_id)
            serializer = self.serializer_class(obj)
            return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, **kwargs):
        try:
            # Extraer el ID del objeto usando nombres de parámetros comunes
            obj_id = self._get_object_id_from_kwargs(kwargs)
            print(f"🔍 Intentando actualizar ID: {obj_id}")  # Verificar el ID en consola
            print(f"📥 Datos recibidos: {request.data}")  # Ver los datos que llegan
            
            obj = get_object_or_404(self.model, id=obj_id)
            serializer = self.serializer_class(obj, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                print(f"✅ Actualización exitosa para ID: {obj_id}")
                return Response({"success": True, "message": "Actualización exitosa"}, status=status.HTTP_200_OK)
            
            print(f"❌ Errores de validación: {serializer.errors}")
            return Response({"success": False, "error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def _get_object_id_from_kwargs(self, kwargs):
        """Extrae el ID del objeto de los kwargs usando nombres de parámetros comunes"""
        common_id_params = ['obj_id', 'pk', 'id', 'sistema_id', 'equipo_id', 'ubicacion_id']
        for param in common_id_params:
            if param in kwargs:
                return kwargs[param]
        raise ValueError("No se encontró un parámetro de ID válido en la URL")

''' -------------------------------------------------------------------------------------------------------------------------------------------------------- '''
class BaseDeleteView(APIView):
    model = None
    permission_classes = []
    http_method_names = ['delete']  # Solo permite DELETE

    def delete(self, request, **kwargs):
        """Vista DELETE para eliminar un objeto por su ID"""
        try:
            # Extraer el ID del objeto usando nombres de parámetros comunes
            obj_id = self._get_object_id_from_kwargs(kwargs)
            
            obj = get_object_or_404(self.model, id=obj_id)
            obj_info = self.get_object_info(obj)
            obj.delete()
            
            return Response({
                "success": True,
                "message": f"Registro {obj_info} eliminado exitosamente"
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False,
                "error": f"Error al eliminar registro: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get_object_info(self, obj):
        """Obtiene información descriptiva del objeto para el mensaje de confirmación"""
        # Por defecto usa __str__, las subclases pueden sobrescribir este método
        return str(obj)
    
    def _get_object_id_from_kwargs(self, kwargs):
        """Extrae el ID del objeto de los kwargs usando nombres de parámetros comunes"""
        common_id_params = ['obj_id', 'pk', 'id', 'sistema_id', 'equipo_id', 'ubicacion_id']
        for param in common_id_params:
            if param in kwargs:
                return kwargs[param]
        raise ValueError("No se encontró un parámetro de ID válido en la URL")

''' -------------------------------------------------------------------------------------------------------------------------------------------------------- '''
class BaseRetrieveView(APIView):
    """Vista base para obtener un objeto específico por ID"""
    model = None
    serializer_class = None
    permission_classes = []

    def get(self, request, **kwargs):
        """Obtiene un objeto específico por su ID"""
        try:
            # Extraer el ID del objeto usando nombres de parámetros comunes
            obj_id = self._get_object_id_from_kwargs(kwargs)
            
            # Si el modelo tiene select_related definido, aplicarlo
            queryset = self.get_queryset()
            obj = get_object_or_404(queryset, id=obj_id)
            serializer = self.serializer_class(obj)
            return Response({
                "success": True,
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False,
                "error": f"Error al obtener registro: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get_queryset(self):
        """Queryset base, las subclases pueden sobrescribir para añadir select_related, etc."""
        return self.model.objects.all()
    
    def _get_object_id_from_kwargs(self, kwargs):
        """Extrae el ID del objeto de los kwargs usando nombres de parámetros comunes"""
        common_id_params = ['obj_id', 'pk', 'id', 'sistema_id', 'equipo_id', 'ubicacion_id']
        for param in common_id_params:
            if param in kwargs:
                return kwargs[param]
        raise ValueError("No se encontró un parámetro de ID válido en la URL")

''' -------------------------------------------------------------------------------------------------------------------------------------------------------- '''
class BaseListAllView(APIView):
    """Vista base para listar todos los objetos sin paginación"""
    model = None
    serializer_class = None
    permission_classes = []

    def get(self, request):
        """Lista todos los objetos sin paginación"""
        try:
            ordering = request.GET.get('ordering', self.get_default_ordering())
            
            # Validar ordenamiento
            if ordering not in self.get_allowed_ordering_fields():
                ordering = self.get_default_ordering()
            
            # Obtener queryset optimizado
            queryset = self.get_queryset().order_by(ordering)
            serializer = self.serializer_class(queryset, many=True)
            
            return Response({
                "success": True,
                "results": serializer.data,
                "count": queryset.count()
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False,
                "error": f"Error al obtener registros: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get_queryset(self):
        """Queryset base, las subclases pueden sobrescribir para añadir select_related, etc."""
        return self.model.objects.all()
    
    def get_default_ordering(self):
        """Ordenamiento por defecto"""
        return 'id'
    
    def get_allowed_ordering_fields(self):
        """Campos permitidos para ordenamiento"""
        return ['id', '-id']