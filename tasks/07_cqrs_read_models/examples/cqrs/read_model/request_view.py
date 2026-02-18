"""
RequestView: Read Model (Проекция)

Денормализованная модель для быстрого чтения
Предметная область: ПСО «Юго-Запад»
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class RequestView:
    """
    Read Model: Денормализованная проекция Request
    
    Отличия от Write Model (Request):
    - Все JOINы предзагружены (coordinator_name, group_leader_name)
    - Нет бизнес-логики (только данные)
    - Нет доменных событий
    - Оптимизирована для SELECT
    
    Источник данных:
    - PostgreSQL Materialized View
    - Или обычная таблица request_views (обновляется через события)
    """
    
    # Основные поля
    request_id: str
    status: str  # "DRAFT", "ACTIVE", "COMPLETED"
    
    # Данные координатора (денормализовано)
    coordinator_id: str
    coordinator_name: str
    coordinator_phone: Optional[str] = None
    
    # Данные зоны (денормализовано)
    zone_name: str
    zone_area_km2: float  # Предвычислено
    
    # Данные группы (денормализовано)
    assigned_group_id: Optional[str] = None
    group_leader_name: Optional[str] = None
    group_members_count: Optional[int] = None
    
    # Временные метки
    created_at: datetime
    activated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Дополнительные поля для UI
    duration_minutes: Optional[int] = None  # Предвычислено
    
    def __post_init__(self):
        """Вычисление производных полей"""
        if self.activated_at and self.completed_at:
            delta = self.completed_at - self.activated_at
            self.duration_minutes = int(delta.total_seconds() / 60)


# === ORM Model для RequestView ===

from sqlalchemy import Column, String, Integer, Float, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class RequestViewORM(Base):
    """
    ORM: Таблица request_views
    
    Заполняется через Projection Handlers при обработке событий
    """
    __tablename__ = "request_views"
    
    request_id = Column(String(50), primary_key=True, index=True)
    status = Column(String(20), nullable=False, index=True)
    
    # Coordinator (денормализовано)
    coordinator_id = Column(String(50), nullable=False)
    coordinator_name = Column(String(200), nullable=False)
    coordinator_phone = Column(String(20), nullable=True)
    
    # Zone (денормализовано)
    zone_name = Column(String(50), nullable=False)
    zone_area_km2 = Column(Float, nullable=False)
    
    # Group (денормализовано)
    assigned_group_id = Column(String(50), nullable=True)
    group_leader_name = Column(String(200), nullable=True)
    group_members_count = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False)
    activated_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Derived fields
    duration_minutes = Column(Integer, nullable=True)
