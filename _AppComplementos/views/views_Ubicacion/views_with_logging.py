"""
Vistas extendidas para Ubicación con logging de acciones
"""
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from _AppAdmin.mixins import ActionLogMixin
from .Commands.CreateUbicacionCommand.CreateUbicacionCommand import CreateUbicacionView
from .Commands.UpdateUbicacionCommand.UpdateUbicacionCommand import UpdateUbicacionView
from .Commands.DeleteUbicacionCommand.DeleteUbicacionCommand import DeleteUbicacionView


class CreateUbicacionWithLogging(ActionLogMixin, CreateUbicacionView):
    """
    Vista de creación de ubicación con logging de acciones
    """
    
    def post(self, request, *args, **kwargs):
        # Llamar al método padre para crear la ubicación
        response = super().post(request, *args, **kwargs)
        
        # Si la creación fue exitosa, registrar la acción
        if response.status_code == status.HTTP_201_CREATED and hasattr(response, 'data'):
            try:
                # Obtener el ID de la respuesta
                ubicacion_id = response.data.get('id')
                
                if ubicacion_id:
                    # Obtener el objeto recién creado de la base de datos para tener todos los datos
                    from ...models import Ubicacion
                    ubicacion = Ubicacion.objects.get(id=ubicacion_id)
                    
                    # Registrar la acción usando el mixin
                    self.log_create_action(
                        request=request,
                        affected_type='ubicacion',
                        affected_value=ubicacion.nombre,
                        affected_id=ubicacion_id
                    )
            except Exception as e:
                print(f"Error al registrar acción de crear ubicación: {e}")
        
        return response


class UpdateUbicacionWithLogging(ActionLogMixin, UpdateUbicacionView):
    """
    Vista de actualización de ubicación con logging de acciones
    """
    
    def put(self, request, *args, **kwargs):
        # Obtener ID de la ubicación
        ubicacion_id = kwargs.get('pk') or kwargs.get('obj_id')
        
        # Llamar al método padre para actualizar
        response = super().put(request, *args, **kwargs)
        
        # Si la actualización fue exitosa, registrar la acción
        if response.status_code == status.HTTP_200_OK and ubicacion_id:
            try:
                # Obtener el objeto actualizado para el nombre correcto
                from ...models import Ubicacion
                ubicacion_actualizada = Ubicacion.objects.get(id=ubicacion_id)
                
                # Registrar la acción usando el mixin
                self.log_update_action(
                    request=request,
                    affected_type='ubicacion',
                    affected_value=ubicacion_actualizada.nombre,
                    affected_id=ubicacion_id
                )
            except Exception as e:
                print(f"Error al registrar acción de editar ubicación: {e}")
        
        return response
    
    def patch(self, request, *args, **kwargs):
        # Similar lógica para PATCH
        ubicacion_id = kwargs.get('pk') or kwargs.get('obj_id')
        
        response = super().patch(request, *args, **kwargs)
        
        if response.status_code == status.HTTP_200_OK and ubicacion_id:
            try:
                # Obtener el objeto actualizado para el nombre correcto
                from ...models import Ubicacion
                ubicacion_actualizada = Ubicacion.objects.get(id=ubicacion_id)
                
                # Registrar la acción usando el mixin
                self.log_update_action(
                    request=request,
                    affected_type='ubicacion',
                    affected_value=ubicacion_actualizada.nombre,
                    affected_id=ubicacion_id
                )
            except Exception as e:
                print(f"Error al registrar acción de editar ubicación: {e}")
        
        return response


class DeleteUbicacionWithLogging(ActionLogMixin, DeleteUbicacionView):
    """
    Vista de eliminación de ubicación con logging de acciones
    """
    
    def delete(self, request, ubicacion_id):
        # Obtener datos antes de la eliminación para el logging
        try:
            from _AppComplementos.models import Ubicacion
            ubicacion = Ubicacion.objects.get(id=ubicacion_id)
            ubicacion_nombre = getattr(ubicacion, 'nombre', getattr(ubicacion, 'name', 'Sin nombre'))
        except Exception:
            ubicacion_nombre = 'Desconocido'
        
        # Llamar al método padre para eliminar
        response = super().delete(request, ubicacion_id)
        
        # Si la eliminación fue exitosa, registrar la acción
        if isinstance(response, Response) and response.status_code == status.HTTP_200_OK:
            try:
                # Registrar la acción usando el mixin
                self.log_delete_action(
                    request=request,
                    affected_type='ubicacion',
                    affected_value=ubicacion_nombre,
                    affected_id=ubicacion_id
                )
            except Exception as e:
                print(f"Error al registrar acción de inactivar ubicación: {e}")
        
        return response