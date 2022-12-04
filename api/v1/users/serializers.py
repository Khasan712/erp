import email
from api.v1.users.models import User
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import ValidationError


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Customizes JWT default Serializer to add more information about user"""
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        if not user.is_varified:
            raise ValidationError("You have to varify your email")
        else:
            token['role'] = user.role
            token['email'] = user.email
            return token


class UserRegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )
    email = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    phone = serializers.CharField(required=True)
    organization = serializers.CharField(required=True)
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'email', 'phone', 'role', 'street', 'city', 'country', 'organization',
            'password', 'password2'
        )

        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        email = validated_data.get('email')
        password = validated_data.get('password')
        password2 = validated_data.get('password2')
        user = User.objects.filter(email=email).first()
        if user:
            raise serializers.ValidationError(
                {
                    "success": False,
                    "message": 'Error occurred.',
                    "error": 'You have already registered.',
                    "data": [],
                }
            )
        if password != password2:
            raise serializers.ValidationError(
                {
                    "success": False,
                    "message": 'Error occurred.',
                    "error": 'The two passwords different.',
                    "data": [],
                }
            )
        user = User(
            first_name=validated_data.get("first_name"),
            last_name=validated_data.get("last_name"),
            country=validated_data.get("country"),
            city=validated_data.get("city"),
            street=validated_data.get("street"),
            email=validated_data.get("email"),
            phone=validated_data.get("phone"),
            role=validated_data.get("role"),
            organization_id=validated_data.get("organization"),
        )
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = (
            'is_staff', 'is_admin', 'is_superuser', 'last_login', 'user_permissions', 'groups', 'is_active', 'password',
            'organization'
        )


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs
    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail('bad_token')







class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('password', 'is_active', 'is_admin', 'is_superuser', 'is_staff')