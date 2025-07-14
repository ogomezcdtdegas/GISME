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

class BaseListAllView(APIView):
    model = None  # 🔹 Se define en la subclase
    serializer_class = None
    template_name = None  # 🔹 Para renderizado en HTML (opcional)

    def get(self, request):
        # Obtener el ordenamiento desde los parámetros de la URL
        ordering = request.GET.get('ordering', '-created_at')
        
        # Validar que el campo de ordenamiento sea seguro
        allowed_fields = self.get_allowed_ordering_fields()
        if ordering.lstrip('-') not in allowed_fields:
            ordering = '-created_at'  # Fallback seguro
        
        queryset = self.model.objects.all().order_by(ordering)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            data = self.serializer_class(queryset, many=True).data
            return Response({"results": data}, status=status.HTTP_200_OK)

        return render(request, self.template_name, {"objects": queryset})
    
    def get_allowed_ordering_fields(self):
        """Devuelve los campos permitidos para ordenamiento. Override en subclases."""
        return ['created_at', 'name']

''' -------------------------------------------------------------------------------------------------------------------------------------------------------- '''

class BaseListView(APIView):
    model = None  # 🔹 Se define en la subclase
    serializer_class = None
    template_name = None  # 🔹 Para renderizado en HTML

    def get(self, request):
        # Obtener el ordenamiento desde los parámetros de la URL
        ordering = request.GET.get('ordering', '-created_at')
        
        # Validar que el campo de ordenamiento sea seguro
        allowed_fields = self.get_allowed_ordering_fields()
        if ordering.lstrip('-') not in allowed_fields:
            ordering = '-created_at'  # Fallback seguro
        
        queryset = self.model.objects.all()
        
        # Aplicar filtros de búsqueda si están presentes
        search_query = request.GET.get('search', '').strip()
        if search_query:
            queryset = self.apply_search_filters(queryset, search_query)
        
        queryset = queryset.order_by(ordering)
        per_page = int(request.GET.get('per_page', 10))
        page_number = int(request.GET.get('page', 1))

        paginator = Paginator(queryset, per_page)
        page_obj = paginator.get_page(page_number)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            data = self.serializer_class(page_obj, many=True).data
            return Response({
                "results": data,
                "has_previous": page_obj.has_previous(),
                "has_next": page_obj.has_next(),
                "previous_page_number": page_obj.previous_page_number() if page_obj.has_previous() else None,
                "next_page_number": page_obj.next_page_number() if page_obj.has_next() else None,
                "current_page": page_obj.number,
                "total_pages": paginator.num_pages,
                "search_query": search_query,  # Incluir el término de búsqueda en la respuesta
            }, status=status.HTTP_200_OK)

        return render(request, self.template_name, {"objects": page_obj})
    
    def get_allowed_ordering_fields(self):
        """Devuelve los campos permitidos para ordenamiento. Override en subclases."""
        return ['created_at', 'name']
    
    def apply_search_filters(self, queryset, search_query):
        """Aplica filtros de búsqueda al queryset. Override en subclases para búsqueda personalizada."""
        # Implementación por defecto: buscar en el campo 'name' si existe
        if hasattr(self.model, 'name'):
            queryset = queryset.filter(name__icontains=search_query)
        return queryset

''' XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX '''


''' XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX '''
''' --------------------------------------------------------------------- Commands ------------------------------------------------------------------------- '''
''' -------------------------------------------------------------------------------------------------------------------------------------------------------- '''
class BaseCreateView(APIView):
    model = None
    serializer_class = None

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

    def get(self, request, obj_id):
        """Vista GET para obtener un objeto por su ID"""
        print(f"🔍 Obteniendo objeto ID: {obj_id}")
        try:
            obj = get_object_or_404(self.model, id=obj_id)
            serializer = self.serializer_class(obj)
            return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, obj_id):
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
''' XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX '''