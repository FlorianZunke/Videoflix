from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from api.serializers import RegisterSerializer




class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "User registered successfully. Activation email sent.",
                "uid": getattr(user, 'activation_uid', ''),
                "token": getattr(user, 'activation_token', '')
            }, status=201)
        return Response(serializer.errors, status=400)