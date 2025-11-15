from aio_pika.abc import AbstractConnection, AbstractChannel, AbstractExchange, AbstractQueue
from aio_pika import connect_robust, ExchangeType, Message
from app.core.Config import get_settings
from typing import Callable, Optional, Dict, Any
from typing import Optional
import aio_pika
import asyncio
import json
import logging

logger = logging.getLogger(__name__)

class QueueManager:
    def __init__(self,settings = None):
        self.settings = settings or get_settings()

        self.connection : Optional[AbstractConnection] = None
        self.channel : Optional[AbstractChannel] = None

        self.exchanges: Dict[str, AbstractExchange] = {}
        self.queues: Dict[str, AbstractQueue] = {}

        self.rabbitmq_host = 'localhost'
        self.rabbitmq_port = 5672
        self.rabbitmq_user = self.settings.RABBITMQ_DEFAULT_USER
        self.rabbitmq_password = self.settings.RABBITMQ_DEFAULT_PASS
        
        logger.info("QueueManager initialized with configuration")
    
    async def connect(self):

        if self.connection and not self.connection.is_closed:
            logger.info("Already connected to RabbitMQ")
            return
        
        try:
            rabbitmq_url = f"amqp://{self.rabbitmq_user}:{self.rabbitmq_password}@{self.rabbitmq_host}:{self.rabbitmq_port}/"
            self.connection = await connect_robust(rabbitmq_url) # reconnection automatique
            self.channel = await self.connection.channel()
            
            await self.channel.set_qos(prefetch_count=10)
            
            logger.info(f" Successfully connected to RabbitMQ at {self.rabbitmq_host}:{self.rabbitmq_port}")
            
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
            raise

    async def setup_broker(self):
        if not self.channel:
            raise RuntimeError("Must call connect() before setup_broker()")
        
        try:
            # 1. Déclarer les exchanges
            await self._declare_exchanges()
            # 2. Déclarer les queues
            await self._declare_queues()
            
            # 3. Créer les bindings (liaisons)
            await self._create_bindings()
            
            logger.info(" Broker setup completed successfully")
            
        except Exception as e:
            logger.error(f" Failed to setup broker: {e}")
            raise
    
    async def _declare_exchanges(self):
        exchanges_config = {
            'market_data_exchange': ExchangeType.TOPIC,# categoris les donnees(market_data.eurusd,market_data.btcusd)selon le "modèle de liaison" (binding pattern) correspond a routing key 
            'indicator_exchange': ExchangeType.FANOUT,   
            'alert_exchange': ExchangeType.DIRECT    
        }
        
        for exchange_name, exchange_type in exchanges_config.items():
            exchange = await self.channel.declare_exchange(
                exchange_name,
                exchange_type,
                durable=True  

            )
            self.exchanges[exchange_name] = exchange
            logger.info(f" Exchange '{exchange_name}' ({exchange_type.value}) declared")

    async def _declare_queues(self):
        """Déclare toutes les queues nécessaires."""
        queues_config = [
            'indicator_queue',     
            'database_saver_queue', 
            'context_aggregator_queue',
            'alert_queue',          
            'backtest_queue'       
        ]
        
        for queue_name in queues_config:
            queue = await self.channel.declare_queue(
                queue_name,
                durable=True,  
                arguments={'x-message-ttl': 3600000}  
            )
            self.queues[queue_name] = queue
            logger.info(f" Queue '{queue_name}' declared")

    async def _create_bindings(self):
        bindings = [
            ('market_data_exchange', 'indicator_queue', 'market_data.*'),
            ('market_data_exchange', 'database_saver_queue', 'market_data.*'),
            ('market_data_exchange', 'context_aggregator_queue', 'market_data.*'),

            
            ('indicator_exchange', 'alert_queue', ''),
            
            ('alert_exchange', 'alert_queue', 'high_priority')
        ]
        
        for exchange_name, queue_name, routing_key in bindings:
            await self.queues[queue_name].bind(
                self.exchanges[exchange_name],
                routing_key
            )
            logger.info(f" Bound '{queue_name}' to '{exchange_name}' with key '{routing_key}'")

    async def publish(self, exchange_name: str, message: Dict[str, Any], routing_key: str = ""):

        if not self.channel:
            raise RuntimeError("Must call connect() before publishing")
        
        try:
            json_message = json.dumps(message, default=str)
            
            message_bytes = json_message.encode('utf-8')
            
            # 3. Créer le message RabbitMQ avec propriétés
            rabbitmq_message = Message(
                message_bytes,
                delivery_mode=2,  
                timestamp=asyncio.get_event_loop().time()
            )
            
            exchange = self.exchanges.get(exchange_name)
            if not exchange:
                raise ValueError(f"Exchange '{exchange_name}' not found. Call setup_broker() first.")
            
            await exchange.publish(rabbitmq_message, routing_key=routing_key)
            
            logger.debug(f" Message published to '{exchange_name}' with key '{routing_key}'")
            
        except Exception as e:
            logger.error(f" Failed to publish message: {e}")
            raise
    async def consume(self, queue_name: str, on_message_callback: Callable[[Dict[str, Any]], None]):
        """
        Commence à consommer une queue. Interface simple pour les consommateurs.
        
        Args:
            queue_name: Nom de la queue à écouter
            on_message_callback: Fonction à appeler pour chaque message reçu
        """
        if not self.channel:
            raise RuntimeError("Must call connect() before consuming")
        
        queue = self.queues.get(queue_name)
        if not queue:
            raise ValueError(f"Queue '{queue_name}' not found. Call setup_broker() first.")
        
        async def message_handler(message: aio_pika.IncomingMessage):
            """Handler interne qui décode et traite chaque message."""
            try:
                # 1. Décoder de bytes en string
                json_string = message.body.decode('utf-8')
                
                # 2. Parser le JSON en dictionnaire Python
                message_data = json.loads(json_string)
                
                # 3. Appeler le callback du consommateur
                await on_message_callback(message_data)
                
                # 4. Acquitter le message (confirmer la réception)
                await message.ack()
                
                logger.debug(f" Message processed from '{queue_name}'")
                
            except Exception as e:
                logger.error(f" Error processing message from '{queue_name}': {e}")
                # Rejeter le message (il sera remis en queue ou envoyé en DLQ)
                await message.nack(requeue=False)
        
        # Commencer la consommation
        await queue.consume(message_handler)
        logger.info(f" Started consuming from '{queue_name}'")

    async def close(self):
        """
        Ferme proprement la connexion RabbitMQ.
        À appeler lors de l'arrêt de l'application.
        """
        try:
            if self.connection and not self.connection.is_closed:
                await self.connection.close()
                logger.info(" RabbitMQ connection closed")
        except Exception as e:
            logger.error(f" Error closing RabbitMQ connection: {e}")

    async def health_check(self) -> bool:
        """
        Vérifie si la connexion RabbitMQ est saine.
        Utile pour les health checks de l'application.
        """
        try:
            return self.connection and not self.connection.is_closed
        except:
            return False