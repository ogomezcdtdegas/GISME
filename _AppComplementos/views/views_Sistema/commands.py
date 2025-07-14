from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db import IntegrityError
from django.core.exceptions import ValidationError

from ...models import Sistema, Ubicacion
from ...serializers import SistemaSerializer
from repoGenerico.views_base import BaseRetrieveUpdateView


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_sistema_command(request):
    """Command para crear un nuevo sistema"""
    try:
        print(f"📥 Datos recibidos para crear sistema: {request.data}")
        
        serializer = SistemaSerializer(data=request.data)
        if serializer.is_valid():
            sistema = serializer.save()
            print(f"✅ Sistema creado exitosamente: {sistema}")
            
            return Response({
                'success': True,
                'data': SistemaSerializer(sistema).data,
                'message': 'Sistema creado exitosamente'
            }, status=status.HTTP_201_CREATED)
        else:
            print(f"❌ Errores de validación: {serializer.errors}")
            return Response({
                'success': False,
                'error': 'Datos inválidos',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except IntegrityError as e:
        error_msg = str(e)
        if 'unique constraint' in error_msg.lower():
            return Response({
                'success': False,
                'error': 'Ya existe un sistema con estos datos (Tag, ID Sistema y Ubicación)'
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'success': False,
                'error': f'Error de integridad en la base de datos: {error_msg}'
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"❌ Error al crear sistema: {str(e)}")
        return Response({
            'success': False,
            'error': f'Error al crear sistema: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def editar_sistema_command(request, sistema_id):
    """Command para editar un sistema existente"""
    try:
        print(f"📝 Editando sistema {sistema_id} con datos: {request.data}")
        
        sistema = Sistema.objects.get(id=sistema_id)
        serializer = SistemaSerializer(sistema, data=request.data, partial=True)
        
        if serializer.is_valid():
            sistema_actualizado = serializer.save()
            print(f"✅ Sistema actualizado exitosamente: {sistema_actualizado}")
            
            return Response({
                'success': True,
                'data': SistemaSerializer(sistema_actualizado).data,
                'message': 'Sistema actualizado exitosamente'
            })
        else:
            print(f"❌ Errores de validación: {serializer.errors}")
            return Response({
                'success': False,
                'error': 'Datos inválidos',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Sistema.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Sistema no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    except IntegrityError as e:
        error_msg = str(e)
        if 'unique constraint' in error_msg.lower():
            return Response({
                'success': False,
                'error': 'Ya existe un sistema con estos datos (Tag, ID Sistema y Ubicación)'
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'success': False,
                'error': f'Error de integridad en la base de datos: {error_msg}'
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"❌ Error al editar sistema: {str(e)}")
        return Response({
            'success': False,
            'error': f'Error al editar sistema: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def eliminar_sistema_command(request, sistema_id):
    """Command para eliminar un sistema"""
    try:
        print(f"🗑️ Eliminando sistema {sistema_id}")
        
        sistema = Sistema.objects.get(id=sistema_id)
        sistema_info = f"{sistema.tag} - {sistema.sistema_id}"
        sistema.delete()
        
        print(f"✅ Sistema eliminado exitosamente: {sistema_info}")
        
        return Response({
            'success': True,
            'message': f'Sistema {sistema_info} eliminado exitosamente'
        })
        
    except Sistema.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Sistema no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"❌ Error al eliminar sistema: {str(e)}")
        return Response({
            'success': False,
            'error': f'Error al eliminar sistema: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SistemaBaseView(BaseRetrieveUpdateView):
    """Vista base para debugging de sistemas"""
    model = Sistema
    serializer_class = SistemaSerializer
    template_name = '_AppComplementos/templates_sistema/debug.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['debug_info'] = f"Sistema ID: {self.kwargs.get('pk', 'N/A')}"
        return context
