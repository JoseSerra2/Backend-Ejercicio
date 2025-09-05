from rest_framework import serializers
from .models import Role, CustomUser, Client
from django.contrib.auth.hashers import make_password

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

class CustomUserSerializer(serializers.ModelSerializer):
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), write_only=True)
    role_detail = RoleSerializer(source='role', read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'user_id',
            'username',
            'email',
            'password',
            'state',
            'role',          # Para creación/actualización: solo ID
            'role_detail',   # Para mostrar detalle del role en GET
            'created_at',
            'updated_at',
            'is_active',
            'is_staff',
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'