"""
Vistas extendidas para Sistema con logging de acciones
"""
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from _AppAdmin.mixins import ActionLogMixin
from .Commands.CreateSistemaCommand.CreateSistemaCommand import CrearSistemaCommandView
from .Commands.UpdateSistemaCommand.UpdateSistemaCommand import EditarSistemaCommandView
from .Commands.DeleteSistemaCommand.DeleteSistemaCommand import EliminarSistemaCommandView


class CreateSistemaWithLogging(ActionLogMixin, CrearSistemaCommandView):
    """
    Vista de creación de sistema con logging de acciones
    """
    
    def post(self, request, *args, **kwargs):
        # Llamar al método padre para crear el sistema
        response = super().post(request, *args, **kwargs)
        
        # Si la creación fue exitosa, registrar la acción
        if response.status_code == status.HTTP_201_CREATED and hasattr(response, 'data'):
            try:
                # Obtener el ID del sistema de la respuesta
                sistema_id = response.data.get('id')
                
                if sistema_id:
                    # Obtener el objeto recién creado de la base de datos para tener todos los datos
                    from ...models import Sistema
                    sistema = Sistema.objects.get(id=sistema_id)
                    sistema_nombre = f"{sistema.tag} - {sistema.sistema_id}" if sistema.tag and sistema.sistema_id else "Sin identificación"
                    
                    # Registrar la acción usando el mixin
                    self.log_create_action(
                        request=request,
                        affected_type='sistema',
                        affected_value=sistema_nombre,
                        affected_id=sistema_id
                    )
            except Exception as e:
                print(f"Error al registrar acción de crear sistema: {e}")
        
        return response


class UpdateSistemaWithLogging(ActionLogMixin, EditarSistemaCommandView):
    """
    Vista de actualización de sistema con logging de acciones
    """
    
    def put(self, request, *args, **kwargs):
        # Obtener ID del sistema
        sistema_id = kwargs.get('pk') or kwargs.get('sistema_id')
        
        # Llamar al método padre para actualizar
        response = super().put(request, *args, **kwargs)
        
        # Si la actualización fue exitosa, registrar la acción
        if response.status_code == status.HTTP_200_OK and sistema_id:
            try:
                # Obtener el objeto actualizado para los datos correctos
                from ...models import Sistema
                sistema_actualizado = Sistema.objects.get(id=sistema_id)
                sistema_nombre_actualizado = f"{sistema_actualizado.tag} - {sistema_actualizado.sistema_id}" if sistema_actualizado.tag and sistema_actualizado.sistema_id else "Sin identificación"
                
                # Registrar la acción usando el mixin
                self.log_update_action(
                    request=request,
                    affected_type='sistema',
                    affected_value=sistema_nombre_actualizado,
                    affected_id=sistema_id
                )
            except Exception as e:
                print(f"Error al registrar acción de editar sistema: {e}")
        
        return response
    
    def patch(self, request, *args, **kwargs):
        # Similar lógica para PATCH
        sistema_id = kwargs.get('pk') or kwargs.get('sistema_id')
        
        response = super().patch(request, *args, **kwargs)
        
        if response.status_code == status.HTTP_200_OK and sistema_id:
            try:
                # Obtener el objeto actualizado para los datos correctos
                from ...models import Sistema
                sistema_actualizado = Sistema.objects.get(id=sistema_id)
                sistema_nombre_actualizado = f"{sistema_actualizado.tag} - {sistema_actualizado.sistema_id}" if sistema_actualizado.tag and sistema_actualizado.sistema_id else "Sin identificación"
                
                # Registrar la acción usando el mixin
                self.log_update_action(
                    request=request,
                    affected_type='sistema',
                    affected_value=sistema_nombre_actualizado,
                    affected_id=sistema_id
                )
            except Exception as e:
                print(f"Error al registrar acción de editar sistema: {e}")
        
        return response


class DeleteSistemaWithLogging(ActionLogMixin, EliminarSistemaCommandView):
    """
    Vista de eliminación de sistema con logging de acciones
    """
    
    def delete(self, request, *args, **kwargs):
        # Obtener datos antes de la eliminación para el logging
        try:
            sistema_id = kwargs.get('pk') or kwargs.get('sistema_id')
            from _AppComplementos.models import Sistema
            sistema = Sistema.objects.get(id=sistema_id)
            sistema_nombre = f"{sistema.tag} - {sistema.sistema_id}" if sistema.tag and sistema.sistema_id else "Sin identificación"
        except Exception:
            sistema_id = None
            sistema_nombre = 'Desconocido'
        
        # Llamar al método padre para eliminar
        response = super().delete(request, *args, **kwargs)
        
        # Si la eliminación fue exitosa, registrar la acción
        if isinstance(response, Response) and response.status_code == status.HTTP_200_OK and sistema_id:
            try:
                # Registrar la acción usando el mixin
                self.log_delete_action(
                    request=request,
                    affected_type='sistema',
                    affected_value=sistema_nombre,
                    affected_id=sistema_id
                )
            except Exception as e:
                print(f"Error al registrar acción de inactivar sistema: {e}")
        
        return response