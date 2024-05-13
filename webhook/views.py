from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView


class AlertManagerWebhook(APIView):
    renderer_classes = [JSONRenderer]
    permission_classes = []

    def post(self, request, *args, **kwargs):
        data = self.request.data
        print(data)
        return Response(status=status.HTTP_200_OK)
