from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Criticidad
from .serializers import CriticidadSerializer


''' -------------------------------------- '''
''' -------------- Querys ---------------- '''
''' -------------------------------------- '''
class allCriticidadPag(APIView):
    def get(self, request):
        criticidad_list = Criticidad.objects.all().order_by('-created_at')
        per_page = int(request.GET.get('per_page', 10))
        page_number = int(request.GET.get('page', 1))

        paginator = Paginator(criticidad_list, per_page)
        criticidad_page = paginator.get_page(page_number)

        # 🔹 Detectar si es AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            criticidad_data = CriticidadSerializer(criticidad_page, many=True).data
            return Response({
                "criticidad": criticidad_data,
                "has_previous": criticidad_page.has_previous(),
                "has_next": criticidad_page.has_next(),
                "previous_page_number": criticidad_page.previous_page_number() if criticidad_page.has_previous() else None,
                "next_page_number": criticidad_page.next_page_number() if criticidad_page.has_next() else None,
                "current_page": criticidad_page.number,
                "total_pages": paginator.num_pages,
            }, status=status.HTTP_200_OK)
        
        # 🔹 Si no es AJAX, renderizar la página
        return render(request, "_AppComplementos/index.html", {"criticidad": criticidad_page})


''' -------------------------------------- '''
''' -------------- Commands -------------- '''
''' -------------------------------------- '''
class crearCriticidad(APIView):
    def post(self, request):
        serializer = CriticidadSerializer(data=request.data)

        if serializer.is_valid():
            criticidad = serializer.save()
            return Response({
                "success": True,
                "message": "Criticidad registrada con éxito",
                "id": criticidad.id  # 🔹 Devolver el ID
            }, status=status.HTTP_201_CREATED)
        
        return Response({"success": False, "error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)



class editarCriticidad(APIView):
    def put(self, request, criticidad_id):
        criticidad = get_object_or_404(Criticidad, id=criticidad_id)
        serializer = CriticidadSerializer(criticidad, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "message": "Criticidad actualizada con éxito"}, status=status.HTTP_200_OK)
        
        return Response({"success": False, "error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)