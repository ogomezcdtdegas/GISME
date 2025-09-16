"""
Vistas extendidas para AdminUser con logging de acciones
"""
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth.models import User
from _AppAdmin.mixins import ActionLogMixin
from .Commands.CreateAdminUserCommand import CreateAdminUserCommand
from .Commands.UpdateAdminUserCommand import UpdateAdminUserCommand
from .Commands.DeleteAdminUserCommand import DeleteAdminUserCommand


class CreateAdminUserWithLogging(ActionLogMixin, CreateAdminUserCommand):
    """
    Vista de creación de usuario administrativo con logging de acciones
    """
    
    def post(self, request, *args, **kwargs):
        # Llamar al método padre para crear el usuario
        response = super().post(request, *args, **kwargs)
        
        # Si la creación fue exitosa, registrar la acción
        if response.status_code == status.HTTP_201_CREATED and hasattr(response, 'data'):
            try:
                # Obtener el ID del usuario de la respuesta
                user_id = response.data.get('id')
                
                if user_id:
                    # Obtener el objeto recién creado de la base de datos para tener todos los datos
                    user = User.objects.get(id=user_id)
                    
                    # Registrar la acción usando el mixin
                    self.log_create_action(
                        request=request,
                        affected_type='usuario',
                        affected_value=user.email,
                        affected_id=user_id
                    )
            except Exception as e:
                print(f"Error al registrar acción de crear usuario: {e}")
        
        return response


class UpdateAdminUserWithLogging(ActionLogMixin, UpdateAdminUserCommand):
    """
    Vista de actualización de usuario administrativo con logging de acciones
    """
    
    def put(self, request, *args, **kwargs):
        # Obtener ID del usuario
        user_id = kwargs.get('pk')
        
        # Llamar al método padre para actualizar
        response = super().put(request, *args, **kwargs)
        
        # Si la actualización fue exitosa, registrar la acción
        if response.status_code == status.HTTP_200_OK and user_id:
            try:
                # Obtener el objeto actualizado para el email correcto
                user_actualizado = User.objects.get(id=user_id)
                
                # Registrar la acción usando el mixin
                self.log_update_action(
                    request=request,
                    affected_type='usuario',
                    affected_value=user_actualizado.email,
                    affected_id=user_id
                )
            except Exception as e:
                print(f"Error al registrar acción de editar usuario: {e}")
        
        return response
    
    def patch(self, request, *args, **kwargs):
        # Similar lógica para PATCH
        user_id = kwargs.get('pk')
        
        response = super().patch(request, *args, **kwargs)
        
        if response.status_code == status.HTTP_200_OK and user_id:
            try:
                # Obtener el objeto actualizado para el email correcto
                user_actualizado = User.objects.get(id=user_id)
                
                # Registrar la acción usando el mixin
                self.log_update_action(
                    request=request,
                    affected_type='usuario',
                    affected_value=user_actualizado.email,
                    affected_id=user_id
                )
            except Exception as e:
                print(f"Error al registrar acción de editar usuario: {e}")
        
        return response


class DeleteAdminUserWithLogging(ActionLogMixin, DeleteAdminUserCommand):
    """
    Vista de eliminación de usuario administrativo con logging de acciones
    """
    
    def delete(self, request, *args, **kwargs):
        # Obtener datos antes de la eliminación para el logging
        try:
            user_id = kwargs.get('pk')
            user = User.objects.get(id=user_id)
            user_email = user.email
        except Exception:
            user_id = None
            user_email = 'Desconocido'
        
        # Llamar al método padre para eliminar
        response = super().delete(request, *args, **kwargs)
        
        # Si la eliminación fue exitosa, registrar la acción
        if isinstance(response, Response) and response.status_code == status.HTTP_200_OK and user_id:
            try:
                # Registrar la acción usando el mixin
                self.log_delete_action(
                    request=request,
                    affected_type='usuario',
                    affected_value=user_email,
                    affected_id=user_id
                )
            except Exception as e:
                print(f"Error al registrar acción de inactivar usuario: {e}")
        
        return response