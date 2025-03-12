from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Equipo
from .serializers import EquipoSerializer


''' -------------------------------------- '''
''' -------------- Querys ---------------- '''
''' -------------------------------------- '''
class allEquiposPag(APIView):
    def get(self, request):
        equipos_list = Equipo.objects.all().order_by('-created_at')
        per_page = int(request.GET.get('per_page', 10))
        page_number = int(request.GET.get('page', 1))

        paginator = Paginator(equipos_list, per_page)
        equipos_page = paginator.get_page(page_number)

        # 🔹 Detectar si es AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            equipos_data = EquipoSerializer(equipos_page, many=True).data
            return Response({
                "equipos": equipos_data,
                "has_previous": equipos_page.has_previous(),
                "has_next": equipos_page.has_next(),
                "previous_page_number": equipos_page.previous_page_number() if equipos_page.has_previous() else None,
                "next_page_number": equipos_page.next_page_number() if equipos_page.has_next() else None,
                "current_page": equipos_page.number,
                "total_pages": paginator.num_pages,
            }, status=status.HTTP_200_OK)
        
        # 🔹 Si no es AJAX, renderizar la página
        return render(request, "_AppHome/index.html", {"equipos": equipos_page})


''' -------------------------------------- '''
''' -------------- Commands -------------- '''
''' -------------------------------------- '''
class crearEquipo(APIView):
    def post(self, request):
        serializer = EquipoSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "message": "Equipo registrado con éxito"}, status=status.HTTP_201_CREATED)
        
        return Response({"success": False, "error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class editarEquipo(APIView):
    def put(self, request, equipo_id):
        equipo = get_object_or_404(Equipo, id=equipo_id)
        serializer = EquipoSerializer(equipo, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "message": "Equipo actualizado con éxito"}, status=status.HTTP_200_OK)
        
        return Response({"success": False, "error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)