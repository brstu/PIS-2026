"""
RequestViewRepository: Репозиторий для Read Model

Только чтение (без save/update)
Предметная область: ПСО «Юго-Запад»
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from cqrs.read_model.request_view import RequestView, RequestViewORM


class RequestViewRepository:
    """
    Repository для RequestView (Read Model)
    
    Отличия от RequestRepository (Write Model):
    - Только методы чтения (find_*)
    - Нет save/update (обновление через события)
    - Быстрые запросы без JOINов
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def find_by_id(self, request_id: str) -> Optional[RequestView]:
        """
        Найти RequestView по ID
        
        Преимущество перед Request.find_by_id():
        - Один SELECT вместо нескольких JOINов
        - Все данные уже денормализованы
        """
        orm_view = self.session.query(RequestViewORM).filter_by(
            request_id=request_id
        ).first()
        
        if not orm_view:
            return None
        
        return self._map_to_dto(orm_view)
    
    def find_active_requests(self, limit: int = 100) -> List[RequestView]:
        """
        Найти все активные заявки
        
        Оптимизация:
        - Индекс на status
        - Без JOINов
        """
        orm_views = self.session.query(RequestViewORM).filter_by(
            status="ACTIVE"
        ).limit(limit).all()
        
        return [self._map_to_dto(orm) for orm in orm_views]
    
    def find_by_coordinator(self, coordinator_id: str) -> List[RequestView]:
        """Найти все заявки координатора"""
        orm_views = self.session.query(RequestViewORM).filter_by(
            coordinator_id=coordinator_id
        ).all()
        
        return [self._map_to_dto(orm) for orm in orm_views]
    
    def find_by_zone(self, zone_name: str) -> List[RequestView]:
        """Найти все заявки по зоне"""
        orm_views = self.session.query(RequestViewORM).filter_by(
            zone_name=zone_name
        ).all()
        
        return [self._map_to_dto(orm) for orm in orm_views]
    
    def find_completed_in_last_days(self, days: int) -> List[RequestView]:
        """Найти завершённые заявки за последние N дней"""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        orm_views = self.session.query(RequestViewORM).filter(
            RequestViewORM.status == "COMPLETED",
            RequestViewORM.completed_at >= cutoff_date
        ).all()
        
        return [self._map_to_dto(orm) for orm in orm_views]
    
    def _map_to_dto(self, orm: RequestViewORM) -> RequestView:
        """Преобразовать ORM → DTO"""
        return RequestView(
            request_id=orm.request_id,
            status=orm.status,
            coordinator_id=orm.coordinator_id,
            coordinator_name=orm.coordinator_name,
            coordinator_phone=orm.coordinator_phone,
            zone_name=orm.zone_name,
            zone_area_km2=orm.zone_area_km2,
            assigned_group_id=orm.assigned_group_id,
            group_leader_name=orm.group_leader_name,
            group_members_count=orm.group_members_count,
            created_at=orm.created_at,
            activated_at=orm.activated_at,
            completed_at=orm.completed_at,
            duration_minutes=orm.duration_minutes
        )
