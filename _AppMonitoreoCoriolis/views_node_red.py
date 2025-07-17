from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import NodeRedData
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class NodeRedReceiverView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        token = request.headers.get('X-API-TOKEN')
        if token != settings.NODE_RED_TOKEN:
            return Response({'error': 'Token inválido'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            data = request.data
            # Guardar en la base de datos
            NodeRedData.objects.create(sensor=data.get('sensor'), valor=data.get('valor'))
            print("Datos recibidos desde Node-RED:", data)
            return Response({'success': True, 'received': data})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
