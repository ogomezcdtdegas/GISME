import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class TendenciasConsumer(AsyncWebsocketConsumer):
    """
    Consumer para manejar conexiones WebSocket de datos de tendencias.
    Cada usuario se conecta a un grupo específico por sistema_id.
    """
    
    async def connect(self):
        """Se ejecuta cuando un cliente se conecta"""
        self.sistema_id = self.scope['url_route']['kwargs']['sistema_id']
        self.room_group_name = f'tendencias_{self.sistema_id}'

        # Unirse al grupo del sistema
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        logger.info(f"✅ WebSocket conectado - Usuario unido a grupo: {self.room_group_name}")

    async def disconnect(self, close_code):
        """Se ejecuta cuando un cliente se desconecta"""
        # Salir del grupo
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"❌ WebSocket desconectado - Usuario salió de grupo: {self.room_group_name}")

    async def receive(self, text_data):
        """
        Se ejecuta cuando se recibe un mensaje del cliente.
        Por ahora no necesitamos manejar mensajes entrantes.
        """
        pass

    async def datos_nuevos(self, event):
        """
        Maneja el evento 'datos_nuevos' enviado desde el backend.
        Este método se llama automáticamente cuando se envía un mensaje al grupo.
        """
        datos = event['datos']

        # Enviar datos al WebSocket del cliente
        await self.send(text_data=json.dumps({
            'tipo': 'datos_nuevos',
            'datos': datos,
            'timestamp': event.get('timestamp', None)
        }))
        
        logger.info(f"📤 Datos enviados por WebSocket a grupo: {self.room_group_name}")
