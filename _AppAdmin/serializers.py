# Serializer para User con UserRole
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserRole
from _AppAuth.models import UserLoginLog

class UserLoginLogSerializer(serializers.ModelSerializer):
    """Serializer para los logs de login de usuarios"""
    
    class Meta:
        model = UserLoginLog
        fields = ['email', 'login_datetime', 'ip_address']
        read_only_fields = ['email', 'login_datetime', 'ip_address']

class UserAdminSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField(read_only=True)
    user_role = serializers.SerializerMethodField(read_only=True)
    full_name = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'date_joined', 'is_active', 'role', 'user_role', 'full_name']
        read_only_fields = ['id', 'date_joined', 'user_role', 'full_name', 'role']
    
    def get_role(self, obj):
        """Obtener rol del usuario"""
        if hasattr(obj, 'user_role') and obj.user_role:
            return obj.user_role.role
        return None
    
    def get_user_role(self, obj):
        """Obtener información del rol del usuario"""
        if hasattr(obj, 'user_role') and obj.user_role:
            return {
                'role': obj.user_role.role,
                'display': obj.user_role.get_role_display()
            }
        return None
    
    def get_full_name(self, obj):
        """Obtener nombre completo"""
        return f"{obj.first_name} {obj.last_name}".strip()
    
    def validate_email(self, value):
        """Validar email único"""
        # Para updates, excluir el objeto actual
        if self.instance:
            if User.objects.filter(email=value).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError('Este correo electrónico ya está registrado.')
        else:
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError('Este correo electrónico ya está registrado.')
        return value


class UserAdminCreateSerializer(serializers.ModelSerializer):
    """Serializer específico para crear usuarios admin"""
    role = serializers.ChoiceField(choices=UserRole.ROLE_CHOICES, write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'role']
    
    def validate_email(self, value):
        """Validar email único"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Este correo electrónico ya está registrado.')
        return value
    
    def create(self, validated_data):
        """Crear usuario con rol"""
        role = validated_data.pop('role')
        
        # Crear usuario
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        
        # Establecer contraseña inutilizable (Azure AD)
        user.set_unusable_password()
        user.save()
        
        # Crear rol
        UserRole.objects.create(user=user, role=role)
        
        return user


class UserAdminUpdateSerializer(serializers.ModelSerializer):
    """Serializer específico para actualizar usuarios admin"""
    role = serializers.SerializerMethodField(read_only=True)
    role_update = serializers.ChoiceField(choices=UserRole.ROLE_CHOICES, write_only=True, required=False)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role', 'role_update']
        read_only_fields = ['id', 'role']
        
    def get_role(self, obj):
        """Obtener rol del usuario"""
        if hasattr(obj, 'user_role') and obj.user_role:
            return obj.user_role.role
        return None
    
    def validate_email(self, value):
        """Validar email único"""
        if self.instance:
            if User.objects.filter(email=value).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError('Este correo electrónico ya está registrado.')
        return value
    
    def update(self, instance, validated_data):
        """Actualizar usuario y rol"""
        role = validated_data.pop('role_update', None)
        
        # Actualizar campos del usuario
        instance.email = validated_data.get('email', instance.email)
        instance.username = instance.email  # Mantener username = email
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.save()
        
        # Actualizar rol si se proporciona
        if role:
            user_role, created = UserRole.objects.get_or_create(user=instance)
            user_role.role = role
            user_role.save()
        
        return instance
