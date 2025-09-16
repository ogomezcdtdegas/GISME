"""
Vistas extendidas para AdminUser con logging de acciones
"""
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth.models import User
from _AppAdmin.utils import log_user_action, get_client_ip
from .Commands.CreateAdminUserCommand import CreateAdminUserCommand
from .Commands.UpdateAdminUserCommand import UpdateAdminUserCommand
from .Commands.DeleteAdminUserCommand import DeleteAdminUserCommand


class CreateAdminUserWithLogging(CreateAdminUserCommand):
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
                    user_email = user.email
                    
                    # Registrar la acción
                    log_user_action(
                        user=request.user,
                        action='crear',
                        affected_type='usuario',
                        affected_value=user_email,
                        affected_id=user_id,
                        ip_address=get_client_ip(request)
                    )
                    print(f"DEBUG CREATE USER: Usuario creado y registrado en log: {user_email}")
            except Exception as e:
                print(f"Error al registrar acción de crear usuario: {e}")
        
        return response


class UpdateAdminUserWithLogging(UpdateAdminUserCommand):
    """
    Vista de actualización de usuario administrativo con logging de acciones
    """
    
    def put(self, request, *args, **kwargs):
        # Obtener datos antes de la actualización para el logging
        print(f"DEBUG USER PUT: kwargs = {kwargs}")
        try:
            user_id = kwargs.get('pk')
            print(f"DEBUG USER PUT: user_id = {user_id}")
            # Obtener el objeto directamente de la base de datos
            user = User.objects.get(id=user_id)
            user_email = user.email
            print(f"DEBUG USER PUT: user_email = {user_email}")
        except Exception as e:
            print(f"DEBUG USER PUT: Error obteniendo usuario: {e}")
            user_id = None
            user_email = 'Desconocido'
        
        # Llamar al método padre para actualizar
        response = super().put(request, *args, **kwargs)
        print(f"DEBUG USER PUT: response.status_code = {response.status_code}")
        
        # Si la actualización fue exitosa, registrar la acción
        if response.status_code == status.HTTP_200_OK and user_id:
            try:
                print(f"DEBUG USER PUT: Registrando acción de editar usuario")
                # Obtener el objeto actualizado para el email correcto
                user_actualizado = User.objects.get(id=user_id)
                # Registrar la acción
                log_user_action(
                    user=request.user,
                    action='editar',
                    affected_type='usuario',
                    affected_value=user_actualizado.email,
                    affected_id=user_id,
                    ip_address=get_client_ip(request)
                )
                print(f"DEBUG USER PUT: Acción registrada exitosamente")
            except Exception as e:
                print(f"Error al registrar acción de editar usuario: {e}")
        
        return response
    
    def patch(self, request, *args, **kwargs):
        # Similar lógica para PATCH
        print(f"DEBUG USER PATCH: kwargs = {kwargs}")
        try:
            user_id = kwargs.get('pk')
            print(f"DEBUG USER PATCH: user_id = {user_id}")
            # Obtener el objeto directamente de la base de datos
            user = User.objects.get(id=user_id)
            user_email = user.email
            print(f"DEBUG USER PATCH: user_email = {user_email}")
        except Exception as e:
            print(f"DEBUG USER PATCH: Error obteniendo usuario: {e}")
            user_id = None
            user_email = 'Desconocido'
        
        response = super().patch(request, *args, **kwargs)
        print(f"DEBUG USER PATCH: response.status_code = {response.status_code}")
        
        if response.status_code == status.HTTP_200_OK and user_id:
            try:
                print(f"DEBUG USER PATCH: Registrando acción de editar usuario")
                # Obtener el objeto actualizado para el email correcto
                user_actualizado = User.objects.get(id=user_id)
                log_user_action(
                    user=request.user,
                    action='editar',
                    affected_type='usuario',
                    affected_value=user_actualizado.email,
                    affected_id=user_id,
                    ip_address=get_client_ip(request)
                )
                print(f"DEBUG USER PATCH: Acción registrada exitosamente")
            except Exception as e:
                print(f"Error al registrar acción de editar usuario: {e}")
        
        return response


class DeleteAdminUserWithLogging(DeleteAdminUserCommand):
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
                # Registrar la acción como "inactivar" ya que es una eliminación
                log_user_action(
                    user=request.user,
                    action='inactivar',
                    affected_type='usuario',
                    affected_value=user_email,
                    affected_id=user_id,
                    ip_address=get_client_ip(request)
                )
                print(f"DEBUG DELETE USER: Usuario eliminado y registrado en log: {user_email}")
            except Exception as e:
                print(f"Error al registrar acción de inactivar usuario: {e}")
        
        return response