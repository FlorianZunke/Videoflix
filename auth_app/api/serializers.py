from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

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
            raise serializers.ValidationError("Email already exists")
        return value
    
    def save(self, **kwargs):
        """
        Create a new user with the validated data
        """
        user = User(
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
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        try:
            user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            raise serializers.ValidationError("Bitte überprüfe deine Eingaben und versuche es erneut.")
        
        if not user.check_password(password):
            raise serializers.ValidationError("Bitte überprüfe deine Eingaben und versuche es erneut.")
        
        data = super().validate({"email": user.email, "password": password, "is_active": user.is_active})
        return data