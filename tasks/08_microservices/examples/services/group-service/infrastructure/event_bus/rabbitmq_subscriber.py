"""
RabbitMQ Subscriber: Подписка на события в Group Service

Предметная область: ПСО «Юго-Запад»
"""
import pika
import json
from typing import Callable, Dict, Any


class RabbitMQSubscriber:
    """
    Subscriber для RabbitMQ
    
    Паттерн: Event Bus / Observer
    Ответственность: Подписка на события из других сервисов
    """
    
    def __init__(self, host: str = 'rabbitmq', port: int = 5672,
                 username: str = 'admin', password: str = 'password',
                 queue_name: str = 'group_service_queue'):
        """
        Инициализация подключения к RabbitMQ
        
        Args:
            host: Хост RabbitMQ
            port: Порт
            username: Логин
            password: Пароль
            queue_name: Название очереди для этого сервиса
        """
        credentials = pika.PlainCredentials(username, password)
        parameters = pika.ConnectionParameters(
            host=host,
            port=port,
            credentials=credentials
        )
        
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        
        # Создание exchange
        self.channel.exchange_declare(
            exchange='pso_events',
            exchange_type='topic',
            durable=True
        )
        
        # Создание очереди
        self.queue_name = queue_name
        self.channel.queue_declare(queue=queue_name, durable=True)
        
        print(f"✅ Connected to RabbitMQ at {host}:{port}")
        print(f"📥 Queue: {queue_name}")
        
        # Mapping event_type → handler
        self.handlers: Dict[str, Callable] = {}
    
    def subscribe(self, event_type: str, routing_key: str = None):
        """
        Подписаться на тип события
        
        Args:
            event_type: Тип события (например, "RequestCreated")
            routing_key: Routing key (по умолчанию = event_type)
        
        Usage:
            @subscriber.subscribe("RequestCreated")
            def on_request_created(event: dict):
                print(f"Request created: {event['request_id']}")
        """
        if routing_key is None:
            routing_key = event_type
        
        # Bind queue to exchange with routing key
        self.channel.queue_bind(
            exchange='pso_events',
            queue=self.queue_name,
            routing_key=routing_key
        )
        
        print(f"🔗 Subscribed to: {routing_key}")
        
        # Декоратор
        def decorator(handler: Callable):
            self.handlers[event_type] = handler
            return handler
        
        return decorator
    
    def start_consuming(self):
        """
        Начать прослушивание событий
        
        Блокирующий вызов (запускается в отдельном потоке)
        """
        def callback(ch, method, properties, body):
            try:
                # Десериализация события
                event_data = json.loads(body)
                event_type = event_data.get("event_type")
                
                # Вызов handler
                handler = self.handlers.get(event_type)
                if handler:
                    handler(event_data["payload"])
                else:
                    print(f"⚠️ No handler for event: {event_type}")
                
                # Acknowledgment
                ch.basic_ack(delivery_tag=method.delivery_tag)
            
            except Exception as e:
                print(f"❌ Error processing event: {e}")
                # Negative acknowledgment (можно переместить в Dead Letter Queue)
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        
        self.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=callback
        )
        
        print("📥 Listening for events...")
        self.channel.start_consuming()
    
    def close(self):
        """Закрыть соединение"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            print("🔌 RabbitMQ connection closed")


# === Пример использования ===

if __name__ == "__main__":
    # Инициализация subscriber
    subscriber = RabbitMQSubscriber(
        host='localhost',
        queue_name='group_service_queue'
    )
    
    # Подписка на событие "RequestCreated"
    @subscriber.subscribe("RequestCreated")
    def on_request_created(payload: dict):
        request_id = payload["request_id"]
        coordinator_id = payload["coordinator_id"]
        zone_name = payload["zone_name"]
        
        print(f"📬 Request created: {request_id}")
        print(f"   Coordinator: {coordinator_id}")
        print(f"   Zone: {zone_name}")
        
        # Бизнес-логика Group Service
        # 1. Найти готовую группу
        # 2. Опубликовать событие "GroupReady"
    
    # Запуск прослушивания
    try:
        subscriber.start_consuming()
    except KeyboardInterrupt:
        print("\n⏹️  Stopping subscriber...")
        subscriber.close()
