from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from auth_app.models import CustomUser

class RegisterSerializer(serializers.ModelSerializer):
    """
    Registration serializer for user sign up
    """

    confirmed_password = serializers.CharField(write_only=True)
    class Meta:
        model = CustomUser
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
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value
    
    def save(self, **kwargs):
        """
        Create a new user with the validated data
        """
        user = CustomUser(
            username=self.validated_data['email'],
            email=self.validated_data['email'],
            is_active=False
        )
        user.set_password(self.validated_data['password'])
        user.save()
        
        # Generate activation token and uid for email verification
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        user.activation_token = token
        user.activation_uid = uid
        
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom serializer to include user data in the token response.
    """
    username_field = 'email'
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get(self.username_field)
        password = attrs.get("password")

        try:
            user = CustomUser.objects.get(**{self.username_field: email})
            if not user.is_active:
                raise serializers.ValidationError("Dein Konto ist nicht aktiv. Bitte aktiviere es.")
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Bitte überprüfe deine Eingaben und versuche es erneut.")
        
        if not user.check_password(password):
            raise serializers.ValidationError("Bitte überprüfe deine Eingaben und versuche es erneut.")
        
        data = super().validate(attrs)
        self.user = user
        return data
    
class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer for initiating password reset
    """
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for confirming password reset
    """
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirmed_password = serializers.CharField(write_only=True, min_length=8)


    def validate(self, data):
        """
        Validate that the new password and confirmed password match
        """
        if data['new_password'] != data['confirmed_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data