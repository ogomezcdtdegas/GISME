from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import NodeRedData
from .serializers import NodeRedDataSerializer
from repoGenerico.views_base import BasicNodeRedAuthMixin, BaseCreateView
from _AppComplementos.models import Sistema, ConfiguracionCoeficientes

@method_decorator(csrf_exempt, name='dispatch')
class NodeRedReceiverView(BasicNodeRedAuthMixin, BaseCreateView):
    model = NodeRedData
    serializer_class = NodeRedDataSerializer
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        auth_error = self.check_basic_auth(request)
        if auth_error:
            return auth_error

        mac_gateway = request.data.get("mac_gateway")
        sistema = Sistema.objects.filter(sistema_id=mac_gateway).first()
        if not mac_gateway or not sistema:
            return Response(
                {"detail": "mac_gateway no registrado como sistema_id en sistemas."},
                status=400
            )

        # Copia los datos y agrega el systemId
        data = request.data.copy()
        data['systemId'] = str(sistema.id)  # UUID a string

        # Obtener coeficientes de corrección vigentes al momento del registro
        try:
            coef = ConfiguracionCoeficientes.objects.get(systemId=sistema)
            data['mt'] = coef.mt
            data['bt'] = coef.bt
            data['mp'] = coef.mp
            data['bp'] = coef.bp
        except ConfiguracionCoeficientes.DoesNotExist:
            # Valores por defecto si no hay coeficientes configurados
            data['mt'] = 1.0
            data['bt'] = 0.0
            data['mp'] = 1.0
            data['bp'] = 0.0

        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            obj = serializer.save()
            return Response({
                "success": True,
                "message": "Registro exitoso",
                "id": obj.id
            }, status=201)
        
        return Response({"success": False, "error": serializer.errors}, status=400)