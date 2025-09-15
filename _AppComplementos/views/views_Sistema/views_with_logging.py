"""
Vistas extendidas para Sistema con logging de acciones
"""
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from _AppAdmin.utils import log_user_action, get_client_ip
from .Commands.CreateSistemaCommand.CreateSistemaCommand import CrearSistemaCommandView
from .Commands.UpdateSistemaCommand.UpdateSistemaCommand import EditarSistemaCommandView
from .Commands.DeleteSistemaCommand.DeleteSistemaCommand import EliminarSistemaCommandView


class CreateSistemaWithLogging(CrearSistemaCommandView):
    """
    Vista de creación de sistema con logging de acciones
    """
    
    def post(self, request, *args, **kwargs):
        # Llamar al método padre para crear el sistema
        response = super().post(request, *args, **kwargs)
        
        # Si la creación fue exitosa, registrar la acción
        if response.status_code == status.HTTP_201_CREATED and hasattr(response, 'data'):
            try:
                # Obtener el ID de la respuesta
                sistema_id = response.data.get('id')
                
                if sistema_id:
                    # Obtener el objeto recién creado de la base de datos para tener todos los datos
                    from ...models import Sistema
                    sistema = Sistema.objects.get(id=sistema_id)
                    sistema_nombre = f"{sistema.tag} - {sistema.sistema_id}"
                    
                    # Registrar la acción
                    log_user_action(
                        user=request.user,
                        action='crear',
                        affected_type='sistema',
                        affected_value=sistema_nombre,
                        affected_id=sistema_id,
                        ip_address=get_client_ip(request)
                    )
            except Exception as e:
                print(f"Error al registrar acción de crear sistema: {e}")
        
        return response


class UpdateSistemaWithLogging(EditarSistemaCommandView):
    """
    Vista de actualización de sistema con logging de acciones
    """
    
    def put(self, request, *args, **kwargs):
        # Obtener datos antes de la actualización para el logging
        try:
            sistema_id = kwargs.get('pk')
            sistema = self.get_object()
            sistema_nombre = f"{sistema.tag} - {sistema.sistema_id}" if sistema.tag and sistema.sistema_id else "Sin identificación"
        except Exception:
            sistema_id = None
            sistema_nombre = 'Desconocido'
        
        # Llamar al método padre para actualizar
        response = super().put(request, *args, **kwargs)
        
        # Si la actualización fue exitosa, registrar la acción
        if response.status_code == status.HTTP_200_OK and sistema_id:
            try:
                # Registrar la acción
                log_user_action(
                    user=request.user,
                    action='editar',
                    affected_type='sistema',
                    affected_value=sistema_nombre,
                    affected_id=sistema_id,
                    ip_address=get_client_ip(request)
                )
            except Exception as e:
                print(f"Error al registrar acción de editar sistema: {e}")
        
        return response
    
    def patch(self, request, *args, **kwargs):
        # Similar lógica para PATCH
        try:
            sistema_id = kwargs.get('pk')
            sistema = self.get_object()
            sistema_nombre = f"{sistema.tag} - {sistema.sistema_id}" if sistema.tag and sistema.sistema_id else "Sin identificación"
        except Exception:
            sistema_id = None
            sistema_nombre = 'Desconocido'
        
        response = super().patch(request, *args, **kwargs)
        
        if response.status_code == status.HTTP_200_OK and sistema_id:
            try:
                log_user_action(
                    user=request.user,
                    action='editar',
                    affected_type='sistema',
                    affected_value=sistema_nombre,
                    affected_id=sistema_id,
                    ip_address=get_client_ip(request)
                )
            except Exception as e:
                print(f"Error al registrar acción de editar sistema: {e}")
        
        return response


class DeleteSistemaWithLogging(EliminarSistemaCommandView):
    """
    Vista de eliminación de sistema con logging de acciones
    """
    
    def delete(self, request, *args, **kwargs):
        # Obtener datos antes de la eliminación para el logging
        try:
            sistema_id = kwargs.get('pk')
            sistema = self.get_object()
            sistema_nombre = f"{sistema.tag} - {sistema.sistema_id}" if sistema.tag and sistema.sistema_id else "Sin identificación"
        except Exception:
            sistema_id = None
            sistema_nombre = 'Desconocido'
        
        # Llamar al método padre para eliminar
        response = super().delete(request, *args, **kwargs)
        
        # Si la eliminación fue exitosa, registrar la acción
        if response.status_code == status.HTTP_200_OK and sistema_id:
            try:
                # Registrar la acción como "inactivar" ya que es una eliminación
                log_user_action(
                    user=request.user,
                    action='inactivar',
                    affected_type='sistema',
                    affected_value=sistema_nombre,
                    affected_id=sistema_id,
                    ip_address=get_client_ip(request)
                )
            except Exception as e:
                print(f"Error al registrar acción de inactivar sistema: {e}")
        
        return response