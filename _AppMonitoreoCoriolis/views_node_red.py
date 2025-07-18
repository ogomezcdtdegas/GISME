from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import base64
from .models import NodeRedData

@method_decorator(csrf_exempt, name='dispatch')
class NodeRedReceiverView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Basic '):
            return Response({'error': 'No autorizado'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            encoded_credentials = auth_header.split(' ')[1]
            decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
            username, password = decoded_credentials.split(':', 1)
        except Exception:
            return Response({'error': 'Credenciales mal formateadas'}, status=status.HTTP_401_UNAUTHORIZED)

        if username != settings.NODE_RED_USER or password != settings.NODE_RED_PASS:
            return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            data = request.data
            # Guardar en la base de datos si lo necesitas
            NodeRedData.objects.create(sensor=data.get('sensor'), valor=data.get('valor'))
            print("Datos recibidos desde Node-RED:", data)
            return Response({'success': True, 'received': data})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)