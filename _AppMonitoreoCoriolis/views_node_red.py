
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import NodeRedData
from repoGenerico.views_base import BasicNodeRedAuthMixin

@method_decorator(csrf_exempt, name='dispatch')
class NodeRedReceiverView(BasicNodeRedAuthMixin, APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        auth_error = self.check_basic_auth(request)
        if auth_error:
            return auth_error

        try:
            data = request.data
            NodeRedData.objects.create(sensor=data.get('sensor'), valor=data.get('valor'))
            print("Datos recibidos desde Node-RED:", data)
            return Response({'success': True, 'received': data})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)