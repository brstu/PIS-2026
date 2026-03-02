"""
RabbitMQ Publisher: Публикация событий из Request Service

Предметная область: ПСО «Юго-Запад»
"""
import pika
import json
from typing import Any, Dict
from domain.events.domain_event import DomainEvent


class RabbitMQPublisher:
    """
    Publisher для RabbitMQ

    Паттерн: Event Bus
    Ответственность: Публикация доменных событий в RabbitMQ
    """

    def __init__(self, host: str = 'rabbitmq', port: int = 5672,
                 username: str = 'admin', password: str = 'password'):
        """
        Инициализация подключения к RabbitMQ

        Args:
            host: Хост RabbitMQ (в Docker: 'rabbitmq')
            port: Порт (по умолчанию 5672)
            username: Логин
            password: Пароль
        """
        credentials = pika.PlainCredentials(username, password)
        parameters = pika.ConnectionParameters(
            host=host,
            port=port,
            credentials=credentials
        )

        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

        # Создание exchange типа 'topic'
        self.channel.exchange_declare(
            exchange='pso_events',
            exchange_type='topic',
            durable=True
        )

        print(f"✅ Connected to RabbitMQ at {host}:{port}")

    def publish(self, event: DomainEvent):
        """
        Публикация доменного события

        Args:
            event: Доменное событие (RequestCreated, GroupAssigned, etc.)
        """
        event_type = event.__class__.__name__
        routing_key = event_type  # Например: "RequestCreated"

        payload = self._serialize_event(event)

        self.channel.basic_publish(
            exchange='pso_events',
            routing_key=routing_key,
            body=json.dumps(payload),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Persistent
                content_type='application/json'
            )
        )

        print(f"📤 Event published: {event_type} → {routing_key}")

    def publish_dict(self, event_type: str, payload: Dict[str, Any]):
        """
        Публикация события из словаря (для интеграционных тестов)

        Args:
            event_type: Тип события (routing key)
            payload: Данные события
        """
        self.channel.basic_publish(
            exchange='pso_events',
            routing_key=event_type,
            body=json.dumps(payload),
            properties=pika.BasicProperties(
                delivery_mode=2,
                content_type='application/json'
            )
        )

        print(f"📤 Event published: {event_type}")

    def close(self):
        """Закрыть соединение"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            print("🔌 RabbitMQ connection closed")

    def _serialize_event(self, event: DomainEvent) -> Dict[str, Any]:
        """Преобразовать доменное событие в JSON"""
        return {
            "event_id": event.event_id,
            "event_type": event.__class__.__name__,
            "occurred_at": event.occurred_at.isoformat(),
            "payload": event.to_dict()
        }


# === Пример использования ===

if __name__ == "__main__":
    from domain.events.request_events import RequestCreated
    from datetime import datetime

    # Инициализация publisher
    publisher = RabbitMQPublisher(host='localhost')

    # Создание события
    event = RequestCreated(
        event_id="evt-001",
        occurred_at=datetime.now(),
        request_id="REQ-2024-0001",
        coordinator_id="COORD-1",
        zone_name="North",
        zone_bounds=(52.0, 52.5, 23.5, 24.0)
    )

    # Публикация
    publisher.publish(event)

    # Закрытие соединения
    publisher.close()
