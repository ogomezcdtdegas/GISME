from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import NodeRedData
from django.utils.decorators import method_decorator
import json

# Puedes poner este token en settings.py y leerlo desde allí si lo prefieres
NODE_RED_TOKEN = "VC8NXK1uXwPs-YnTx9EZ5HXtg1B3F5Ml00WecfmTL3pkLh-4WdoX3Lt-rcG1s3pK4VH9L8YWaU7umcvdhb2Tg2wZL149XwK2Vtw-m-W5LWak4ItzF6k6yP1H2L070J-6Xa8EygGCiJzUeyDKZOOaEq3c2xwpoN-HMeBos3Oc4Kc"

@method_decorator(csrf_exempt, name='dispatch')
class NodeRedReceiverView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        token = request.headers.get('X-API-TOKEN')
        if token != NODE_RED_TOKEN:
            return Response({'error': 'Token inválido'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            data = request.data
            # Guardar en la base de datos
            NodeRedData.objects.create(sensor=data.get('sensor'), valor=data.get('valor'))
            print("Datos recibidos desde Node-RED:", data)
            return Response({'success': True, 'received': data})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
