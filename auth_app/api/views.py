
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.encoding import force_bytes
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
import django_rq
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer, PasswordResetSerializer, PasswordResetConfirmSerializer
from core import settings
from .utils import job_send_reset_password_mail

User = get_user_model()
class RegisterView(APIView):
    """ 
    View for user registration
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handle POST requests for user registration.
        """
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "user": {
                    "id": user.id,
                    "email": user.email
                },
                "token": getattr(user, 'activation_token')
            }, status=201)
        return Response(serializer.errors, status=400)
    
class CookieTokenObtainPairView(TokenObtainPairView):
    """
    View for obtaining a cookie-based token pair.
    """
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests for obtaining a cookie-based token pair.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh = serializer.validated_data["refresh"]
        access = serializer.validated_data["access"]

        response = Response({
            "detail": "Login successful",
            "user": {
                "id": serializer.user.id,
                "email": serializer.user.email
            }})

        response.set_cookie(
            key="access_token",
            value=str(access),
            httponly=True,
            secure=True,
            samesite="None"
        )

        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=True,
            samesite="None"
        )

        return response

class CookieTokenRefreshView(TokenRefreshView):
    """
    View for refreshing the access token using a cookie-based refresh token.
    """

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests for refreshing the access token.
        """
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {"error": "Refresh token not found in cookies."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        serializer = self.get_serializer(data={"refresh": refresh_token})

        try:
            serializer.is_valid(raise_exception=True)
        except:
            return Response(
                {"error": "Refresh token invalid!."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        access_token = serializer.validated_data.get("access")

        response = Response({
            "detail": "Token refreshed",
            "access": "new_access_token"
        }, status=status.HTTP_200_OK)

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="None"
        )

        return response

class LogoutView(APIView):
    """
    View for logging out a user by clearing authentication cookies.
    """

    def post(self, request):
        """
        Handle POST requests for logging out a user.
        """
        response = Response(
            {"detail": "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."}, status=status.HTTP_200_OK)
        
        token = RefreshToken(request.COOKIES.get("refresh_token"))
        token.blacklist()
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return response


class ActivateAccountView(APIView):
    """
    View for activating a user account via email link.
    """
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        """
        Handle GET requests for activating a user account.
        """
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
            
            if default_token_generator.check_token(user, token):
                user.is_active = True
                user.save()
                return Response({"message": "Konto erfolgreich aktiviert!"}, status=200)
            else:
                return Response({"error": "Der Aktivierungs-Link ist ungültig oder abgelaufen."}, status=400)

        except (TypeError, ValueError, OverflowError, ObjectDoesNotExist):
            return Response({"error": "Ungültiger Link."}, status=400)


class PasswordResetView(APIView):
    """
    View for handling password reset requests by sending a reset link to the user's email.
    """

    def post(self, request):
        """
        Handle POST requests for password reset by validating the email and sending a reset link.
        """
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.filter(email=email, is_active=True).first()

            if user:
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                
                reset_link = f"{settings.FRONTEND_URL}/pages/auth/confirm_password.html?uid={uid}&token={token}"

                django_rq.enqueue(job_send_reset_password_mail, user.email, reset_link)

            return Response({"detail": "Falls ein Konto existiert, wurde eine E-Mail gesendet."}, status=200)
        
        return Response(serializer.errors, status=400)

class PasswordResetConfirmView(APIView):
    """
    View for confirming password reset by validating the token and setting the new password.
    """
    def post(self, request, uidb64, token):
        """
        Handle POST requests for confirming password reset by validating the token and setting the new password.
        """
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, ObjectDoesNotExist):
            user = None
            
        if user is not None and default_token_generator.check_token(user, token):
            new_password = serializer.validated_data['new_password']
            user.set_password(new_password)
            user.save()
            
            return Response({"detail": "Your Password has been successfully reset."}, status=200)
        else:
            return Response({"detail": "Der Link zur Passwortzurücksetzung ist ungültig oder abgelaufen."}, status=400)