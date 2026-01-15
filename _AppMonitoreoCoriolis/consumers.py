import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class TendenciasConsumer(AsyncWebsocketConsumer):
    """
    Consumer optimizado para manejar conexiones WebSocket con Azure Cache for Redis.
    
    Arquitectura:
    - Cada usuario se conecta a un grupo específico por sistema_id
    - Redis maneja el fanout distribuido a TODOS los workers
    - El consumer solo recibe y reenvía, sin procesamiento pesado
    
    Flujo:
    1. Node-RED → Django View → PostgreSQL
    2. Django View → Redis Pub/Sub (async_to_sync)
    3. Redis → TODOS los consumers suscritos al grupo
    4. Consumer → WebSocket del navegador
    
    Rendimiento:
    - Latencia total: <50ms desde Node-RED hasta el frontend
    - Django responde a Node-RED en ~10-15ms
    - Redis hace fanout en <5ms
    """
    
    async def connect(self):
        """
        Se ejecuta cuando un cliente se conecta.
        Une al usuario al grupo de Redis para recibir actualizaciones en tiempo real.
        """
        try:
            self.sistema_id = self.scope['url_route']['kwargs']['sistema_id']
            self.room_group_name = f'tendencias_{self.sistema_id}'

            # Unirse al grupo de Redis (fanout distribuido)
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()
            logger.info(f"✅ WebSocket conectado - Usuario unido a grupo Redis: {self.room_group_name}")
            
            # Enviar mensaje de confirmación al cliente
            await self.send(text_data=json.dumps({
                'tipo': 'connection_established',
                'message': f'Conectado a sistema {self.sistema_id}',
                'grupo': self.room_group_name,
                'timestamp': None
            }))
            
        except Exception as e:
            logger.error(f"❌ Error al conectar WebSocket: {str(e)}", exc_info=True)
            await self.close()

    async def disconnect(self, close_code):
        """
        Se ejecuta cuando un cliente se desconecta.
        Remueve al usuario del grupo de Redis.
        """
        # Salir del grupo de Redis
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"❌ WebSocket desconectado - Usuario salió de grupo Redis: {self.room_group_name} (código: {close_code})")

    async def receive(self, text_data):
        """
        Se ejecuta cuando se recibe un mensaje del cliente.
        Por ahora no necesitamos manejar mensajes entrantes del navegador.
        """
        pass

    async def datos_nuevos(self, event):
        """
        Maneja el evento 'datos_nuevos' enviado desde Redis.
        
        Este método se llama automáticamente cuando:
        - El endpoint Django publica en Redis con channel_layer.group_send()
        - Redis hace fanout a TODOS los consumers del grupo
        - Este consumer recibe el mensaje y lo reenvía al navegador
        
        Args:
            event (dict): Contiene 'datos' y 'timestamp' del mensaje
        """
        datos = event['datos']

        # Enviar datos al WebSocket del navegador (sin procesamiento adicional)
        await self.send(text_data=json.dumps({
            'tipo': 'datos_nuevos',
            'datos': datos,
            'timestamp': event.get('timestamp', None)
        }))
        
        logger.debug(f"📤 Datos enviados por WebSocket a cliente: {self.channel_name}")
