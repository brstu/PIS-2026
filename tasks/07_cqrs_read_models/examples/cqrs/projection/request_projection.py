"""
RequestProjection: Обработчик событий для синхронизации Read Model

Слушает доменные события и обновляет RequestView
Предметная область: ПСО «Юго-Запад»
"""
from datetime import datetime
from sqlalchemy.orm import Session
from domain.events.request_events import (
    RequestCreated,
    GroupAssignedToRequest,
    RequestActivated,
    RequestCompleted
)
from cqrs.read_model.request_view import RequestViewORM


class RequestProjection:
    """
    Projection Handler: События → RequestView
    
    Паттерн: Event Sourcing Projection
    Ответственность: Синхронизация Write Model и Read Model
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def on_request_created(self, event: RequestCreated):
        """
        Обработка события: RequestCreated
        
        Действие: INSERT в request_views
        """
        # Загрузка дополнительных данных (coordinator, zone)
        coordinator = self._fetch_coordinator_data(event.coordinator_id)
        zone_area = self._calculate_zone_area(event.zone_bounds)
        
        # Создание проекции
        view = RequestViewORM(
            request_id=event.request_id,
            status="DRAFT",
            coordinator_id=event.coordinator_id,
            coordinator_name=coordinator["name"],
            coordinator_phone=coordinator.get("phone"),
            zone_name=event.zone_name,
            zone_area_km2=zone_area,
            assigned_group_id=None,
            group_leader_name=None,
            group_members_count=None,
            created_at=event.occurred_at,
            activated_at=None,
            completed_at=None,
            duration_minutes=None
        )
        
        self.session.add(view)
        self.session.commit()
    
    def on_group_assigned(self, event: GroupAssignedToRequest):
        """
        Обработка события: GroupAssignedToRequest
        
        Действие: UPDATE request_views SET assigned_group_id, group_leader_name, ...
        """
        # Загрузка данных группы
        group_data = self._fetch_group_data(event.group_id)
        
        # Обновление проекции
        view = self.session.query(RequestViewORM).filter_by(
            request_id=event.request_id
        ).first()
        
        if view:
            view.assigned_group_id = event.group_id
            view.group_leader_name = group_data["leader_name"]
            view.group_members_count = group_data["members_count"]
            
            self.session.commit()
    
    def on_request_activated(self, event: RequestActivated):
        """
        Обработка события: RequestActivated
        
        Действие: UPDATE request_views SET status='ACTIVE', activated_at=...
        """
        view = self.session.query(RequestViewORM).filter_by(
            request_id=event.request_id
        ).first()
        
        if view:
            view.status = "ACTIVE"
            view.activated_at = event.occurred_at
            
            self.session.commit()
    
    def on_request_completed(self, event: RequestCompleted):
        """
        Обработка события: RequestCompleted
        
        Действие: UPDATE request_views SET status='COMPLETED', completed_at=..., duration=...
        """
        view = self.session.query(RequestViewORM).filter_by(
            request_id=event.request_id
        ).first()
        
        if view:
            view.status = "COMPLETED"
            view.completed_at = event.occurred_at
            
            # Вычисление длительности операции
            if view.activated_at:
                delta = event.occurred_at - view.activated_at
                view.duration_minutes = int(delta.total_seconds() / 60)
            
            self.session.commit()
    
    # === Helper Methods ===
    
    def _fetch_coordinator_data(self, coordinator_id: str) -> dict:
        """Загрузить данные координатора из Write Model"""
        # В реальности: запрос к coordinators таблице
        return {
            "name": "Иван Иванов",
            "phone": "+375291234567"
        }
    
    def _fetch_group_data(self, group_id: str) -> dict:
        """Загрузить данные группы из Write Model"""
        # В реальности: запрос к groups + volunteers таблицам
        return {
            "leader_name": "Пётр Петров",
            "members_count": 5
        }
    
    def _calculate_zone_area(self, bounds: tuple) -> float:
        """Вычислить площадь зоны в км²"""
        lat_min, lat_max, lon_min, lon_max = bounds
        # Упрощённый расчёт (в реальности: Haversine formula)
        return abs((lat_max - lat_min) * (lon_max - lon_min)) * 12365.0


# === Event Bus Integration ===

class EventBus:
    """
    Event Bus: Публикация событий и вызов projection handlers
    
    Паттерн: Observer / Mediator
    """
    
    def __init__(self, projection: RequestProjection):
        self.projection = projection
        self.handlers = {
            "RequestCreated": self.projection.on_request_created,
            "GroupAssignedToRequest": self.projection.on_group_assigned,
            "RequestActivated": self.projection.on_request_activated,
            "RequestCompleted": self.projection.on_request_completed
        }
    
    def publish(self, event):
        """Публикация события"""
        event_type = event.__class__.__name__
        handler = self.handlers.get(event_type)
        
        if handler:
            handler(event)
        else:
            print(f"⚠️ No handler for event: {event_type}")
