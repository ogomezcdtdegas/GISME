from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.db import models
from _AppAdmin.mixins import ComplementosPermissionMixin

from .....models import ConfiguracionCoeficientes, Sistema
from _AppAdmin.utils import log_user_action, get_client_ip

from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    post=extend_schema(tags=['ConfiguracionCoeficientes']),
)

class CreateOrUpdateCoeficientesCommandView(ComplementosPermissionMixin, APIView):
    """CBV Command para crear o actualizar coeficientes de corrección para un sistema"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Crear o actualizar coeficientes de corrección.
        Si el sistema ya tiene coeficientes, los actualiza. Si no, crea nuevos.
        """
        try:
            # Extraer datos del request
            system_id = request.data.get('systemId')
            mt = request.data.get('mt')
            bt = request.data.get('bt')
            mp = request.data.get('mp')
            bp = request.data.get('bp')
            zero_presion = request.data.get('zero_presion', 0.0)
            span_presion = request.data.get('span_presion', 1.0)
            
            # Nuevos campos de configuración de batch
            lim_inf_caudal_masico = request.data.get('lim_inf_caudal_masico', 0.0)
            lim_sup_caudal_masico = request.data.get('lim_sup_caudal_masico', 1000000.0)
            vol_masico_ini_batch = request.data.get('vol_masico_ini_batch', 0.0)
            num_ticket = request.data.get('num_ticket', 1)
            time_finished_batch = request.data.get('time_finished_batch', 2.0)

            # Campos de Incertidumbre
            mf = request.data.get('mf')
            vis = request.data.get('vis')
            deltavis = request.data.get('deltavis')
            dn = request.data.get('dn')
            ucal_dens = request.data.get('ucal_dens')
            kcal_dens = request.data.get('kcal_dens')
            tipdens = request.data.get('tipdens')
            desv_dens = request.data.get('desv_dens')
            ucal_met = request.data.get('ucal_met')
            kcal_met = request.data.get('kcal_met')
            esis_met = request.data.get('esis_met')
            ucarta_met = request.data.get('ucarta_met')
            zero_stab = request.data.get('zero_stab')

            # Validaciones básicas
            if not system_id:
                return Response({
                    "success": False,
                    "error": "El campo systemId es requerido"
                }, status=status.HTTP_400_BAD_REQUEST)

            if mt is None or bt is None or mp is None or bp is None:
                return Response({
                    "success": False,
                    "error": "Todos los coeficientes (mt, bt, mp, bp) son requeridos"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Verificar que el sistema existe
            try:
                sistema = Sistema.objects.get(id=system_id)
            except Sistema.DoesNotExist:
                return Response({
                    "success": False,
                    "error": "El sistema especificado no existe"
                }, status=status.HTTP_404_NOT_FOUND)

            # Validar num_ticket: debe ser mayor o igual al máximo + 1 en batches
            if num_ticket is not None:
                # Importar aquí para evitar circular imports
                from _AppMonitoreoCoriolis.models import BatchDetectado
                
                max_ticket = BatchDetectado.objects.filter(
                    systemId=sistema,
                    num_ticket__isnull=False
                ).aggregate(models.Max('num_ticket'))['num_ticket__max'] or 0
                
                min_allowed = max_ticket + 1
                if int(num_ticket) < min_allowed:
                    return Response({
                        "success": False,
                        "error": f"El número de ticket debe ser mayor o igual a {min_allowed}. El máximo ticket asignado es {max_ticket}."
                    }, status=status.HTTP_400_BAD_REQUEST)

            # Crear o actualizar coeficientes usando get_or_create
            coeficientes, created = ConfiguracionCoeficientes.objects.get_or_create(
                systemId=sistema,
                defaults={
                    'mt': float(mt),
                    'bt': float(bt),
                    'mp': float(mp),
                    'bp': float(bp),
                    'zero_presion': float(zero_presion),
                    'span_presion': float(span_presion),
                    'lim_inf_caudal_masico': float(lim_inf_caudal_masico),
                    'lim_sup_caudal_masico': float(lim_sup_caudal_masico),
                    'vol_masico_ini_batch': float(vol_masico_ini_batch),
                    'num_ticket': int(num_ticket),
                    'time_finished_batch': float(time_finished_batch),
                    # Incertidumbre (defaults si vienen nulos)
                    'mf': float(mf) if mf is not None and mf != '' else 1.0,
                    'vis': float(vis) if vis is not None and vis != '' else 0.0,
                    'deltavis': float(deltavis) if deltavis is not None and deltavis != '' else 0.0,
                    'dn': float(dn) if dn is not None and dn != '' else 0.0,
                    'ucal_dens': float(ucal_dens) if ucal_dens is not None and ucal_dens != '' else 0.0,
                    'kcal_dens': float(kcal_dens) if kcal_dens is not None and kcal_dens != '' else 0.0,
                    'tipdens': tipdens if tipdens not in [None, ''] else None,
                    'desv_dens': float(desv_dens) if desv_dens is not None and desv_dens != '' else 0.0,
                    'ucal_met': float(ucal_met) if ucal_met is not None and ucal_met != '' else 0.0,
                    'kcal_met': float(kcal_met) if kcal_met is not None and kcal_met != '' else 0.0,
                    'esis_met': float(esis_met) if esis_met is not None and esis_met != '' else 0.0,
                    'ucarta_met': float(ucarta_met) if ucarta_met is not None and ucarta_met != '' else 0.0,
                    'zero_stab': float(zero_stab) if zero_stab is not None and zero_stab != '' else 0.0,
                }
            )

            # Si ya existía, actualizar los valores
            if not created:
                coeficientes.mt = float(mt)
                coeficientes.bt = float(bt)
                coeficientes.mp = float(mp)
                coeficientes.bp = float(bp)
                coeficientes.zero_presion = float(zero_presion)
                coeficientes.span_presion = float(span_presion)
                coeficientes.lim_inf_caudal_masico = float(lim_inf_caudal_masico)
                coeficientes.lim_sup_caudal_masico = float(lim_sup_caudal_masico)
                coeficientes.vol_masico_ini_batch = float(vol_masico_ini_batch)
                coeficientes.num_ticket = int(num_ticket)
                coeficientes.time_finished_batch = float(time_finished_batch)
                # Actualizar incertidumbre solo si vienen en la solicitud
                if mf is not None:
                    coeficientes.mf = float(mf)
                if vis is not None:
                    coeficientes.vis = float(vis)
                if deltavis is not None:
                    coeficientes.deltavis = float(deltavis)
                if dn is not None:
                    coeficientes.dn = float(dn)
                if ucal_dens is not None:
                    coeficientes.ucal_dens = float(ucal_dens)
                if kcal_dens is not None:
                    coeficientes.kcal_dens = float(kcal_dens)
                if tipdens is not None:
                    coeficientes.tipdens = tipdens or None
                if desv_dens is not None:
                    coeficientes.desv_dens = float(desv_dens)
                if ucal_met is not None:
                    coeficientes.ucal_met = float(ucal_met)
                if kcal_met is not None:
                    coeficientes.kcal_met = float(kcal_met)
                if esis_met is not None:
                    coeficientes.esis_met = float(esis_met)
                if ucarta_met is not None:
                    coeficientes.ucarta_met = float(ucarta_met)
                if zero_stab is not None:
                    coeficientes.zero_stab = float(zero_stab)
                coeficientes.save()

            # Registrar la acción en el log universal
            action = 'crear' if created else 'editar'
            log_user_action(
                user=request.user,
                action=action,
                affected_type='sistema',  # Tipo de registro afectado
                affected_value=f'{sistema.tag} - Coeficientes de corrección: {{MT: {coeficientes.mt}, BT: {coeficientes.bt}, MP: {coeficientes.mp}, BP: {coeficientes.bp}, Zero: {coeficientes.zero_presion}, Span: {coeficientes.span_presion}, LimInf: {coeficientes.lim_inf_caudal_masico}, LimSup: {coeficientes.lim_sup_caudal_masico}, VolBatch: {coeficientes.vol_masico_ini_batch}, Ticket: {coeficientes.num_ticket}, TimeBatch: {coeficientes.time_finished_batch}}}',
                affected_id=str(sistema.id),  # ID del sistema afectado
                ip_address=get_client_ip(request)
            )

            return Response({
                "success": True,
                "message": "Coeficientes creados exitosamente" if created else "Coeficientes actualizados exitosamente",
                "created": created,
                "data": {
                    "id": coeficientes.id,
                    "systemId": str(sistema.id),
                    "sistema_tag": sistema.tag,
                    "mt": coeficientes.mt,
                    "bt": coeficientes.bt,
                    "mp": coeficientes.mp,
                    "bp": coeficientes.bp,
                    "lim_inf_caudal_masico": coeficientes.lim_inf_caudal_masico,
                    "lim_sup_caudal_masico": coeficientes.lim_sup_caudal_masico,
                    "vol_masico_ini_batch": coeficientes.vol_masico_ini_batch,
                    "num_ticket": coeficientes.num_ticket,
                    "time_finished_batch": coeficientes.time_finished_batch,
                    # Incertidumbre en respuesta (sin dl manual)
                    "mf": coeficientes.mf,
                    "vis": coeficientes.vis,
                    "deltavis": coeficientes.deltavis,
                    "dn": coeficientes.dn,
                    "ucal_dens": coeficientes.ucal_dens,
                    "kcal_dens": coeficientes.kcal_dens,
                    "tipdens": coeficientes.tipdens,
                    "desv_dens": coeficientes.desv_dens,
                    "ucal_met": coeficientes.ucal_met,
                    "kcal_met": coeficientes.kcal_met,
                    "esis_met": coeficientes.esis_met,
                    "ucarta_met": coeficientes.ucarta_met,
                    "zero_stab": coeficientes.zero_stab,
                }
            }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

        except ValueError as e:
            return Response({
                "success": False,
                "error": f"Error en los valores numéricos: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"❌ Error inesperado en CreateOrUpdateCoeficientesCommandView: {str(e)}")
            return Response({
                "success": False,
                "error": "Error interno del servidor"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)