from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes



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
        
        # Token für Aktivierungs-E-Mail generieren
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        user.activation_token = token
        user.activation_uid = uid
        
        return user
    
class LoginSerializer(serializers.Serializer):
    """
    Login serializer for user authentication
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)