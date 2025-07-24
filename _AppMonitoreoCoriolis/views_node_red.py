

from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import NodeRedData
from .serializers import NodeRedDataSerializer
from repoGenerico.views_base import BasicNodeRedAuthMixin, BaseCreateView

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
        return super().post(request, *args, **kwargs)