from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth import get_user_model, authenticate
from .utils import job_send_activation_mail
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from django.conf import settings


User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    """
    Registration serializer for user sign up
    """

    confirmed_password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['email', 'password', 'confirmed_password']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }

    def validate_confirmed_password(self, value):
        """
        Check that the two password entries match
        """
        data = self.get_initial()
        password = data.get('password')
        confirem_password = value
        if password != confirem_password:
            raise serializers.ValidationError("Passwords do not match")
        return value
    
    def validate_email(self, value):
        """
        Check that the email is unique
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Bitte überprüfe deine Eingaben und versuche es erneut.")
        return value
    
    def save(self, **kwargs):
        user = User.objects.create_user(
            username=self.validated_data['email'],
            email=self.validated_data['email'],
            password=self.validated_data['password'],
            is_active=False
        )
        user.set_password(self.validated_data['password'])
        user.save() 

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        user.activation_token = token
        user.activation_uid = uid

        activation_link = f"{settings.FRONTEND_URL}/pages/auth/activate.html?uid={uid}&token={token}"
        try:
            job_send_activation_mail(user.email, activation_link)
        except Exception as e:
            print(f"Mail-Fehler: {e}")
    
        return user

class CustomTokenObtainPairSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user_obj = User.objects.filter(email=email).first()

        if not user_obj:
            raise serializers.ValidationError({"detail": "Kein Konto mit dieser E-Mail gefunden."})

        if not user_obj.is_active:
            raise serializers.ValidationError({"detail": "Dein Konto ist nicht aktiv. Bitte aktiviere es."})

        user = authenticate(username=email, password=password)

        if user is None:
            raise serializers.ValidationError({"detail": "Falsches Passwort."})

        refresh = RefreshToken.for_user(user)

        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

        self.user = user
        return data
    
class PasswordResetSerializer(serializers.Serializer):
    """
    Validiert nur, ob die E-Mail ein gültiges Format hat.
    """
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Die Passwörter stimmen nicht überein."})
    
        try:
            validate_password(data['new_password'])
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})
            
        return data