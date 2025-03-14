from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

''' -------------------------------------- '''
''' ----------- Base List View ----------- '''
''' -------------------------------------- '''
class BaseListAllView(APIView):
    model = None  # 🔹 Se define en la subclase
    serializer_class = None
    template_name = None  # 🔹 Para renderizado en HTML (opcional)

    def get(self, request):
        queryset = self.model.objects.all().order_by('-created_at')

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            data = self.serializer_class(queryset, many=True).data
            return Response({"results": data}, status=status.HTTP_200_OK)

        return render(request, self.template_name, {"objects": queryset})

class BaseListView(APIView):
    model = None  # 🔹 Se define en la subclase
    serializer_class = None
    template_name = None  # 🔹 Para renderizado en HTML

    def get(self, request):
        queryset = self.model.objects.all().order_by('-created_at')
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
            }, status=status.HTTP_200_OK)

        return render(request, self.template_name, {"objects": page_obj})


''' -------------------------------------- '''
''' ----------- Base Create View ----------- '''
''' -------------------------------------- '''
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


''' -------------------------------------- '''
''' ----------- Base Update View ----------- '''
''' -------------------------------------- '''
class BaseRetrieveUpdateView(APIView):
    model = None
    serializer_class = None

    def put(self, request, obj_id):
        print(f"🔍 Intentando actualizar ID: {obj_id}")  # Verificar el ID en consola
        obj = get_object_or_404(self.model, id=obj_id)
        serializer = self.serializer_class(obj, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "message": "Actualización exitosa"}, status=status.HTTP_200_OK)
        
        return Response({"success": False, "error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
