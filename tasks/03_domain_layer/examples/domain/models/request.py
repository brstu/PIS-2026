"""
Request (Aggregate Root): Заявка на поисково-спасательную операцию

Агрегат объединяет Request, Group, Zone
Предметная область: ПСО «Юго-Запад»
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from domain.models.group import Group
from domain.models.zone import Zone
from domain.models.request_status import RequestStatus
from domain.events.request_events import (
    GroupAssignedToRequest,
    RequestActivated,
    RequestZoneChanged,
    RequestCompleted
)


@dataclass
class Request:
    """
    Агрегат: Заявка на поисково-спасательную операцию
    
    Инварианты:
    1. Нельзя активировать заявку без назначенной группы
    2. Нельзя назначить группу для заявки, которая уже активна/завершена
    3. Нельзя изменить зону для завершённой заявки
    4. Группа должна быть готова (3-5 участников) при назначении
    """
    request_id: str
    coordinator_id: str
    zone: Zone
    status: RequestStatus = field(default_factory=lambda: RequestStatus.DRAFT)
    assigned_group: Optional[Group] = None
    created_at: datetime = field(default_factory=datetime.now)
    activated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    _events: List = field(default_factory=list, repr=False, compare=False)
    
    def assign_group(self, group: Group) -> None:
        """
        Назначить группу на заявку
        
        Инварианты:
        - Статус должен быть DRAFT
        - Группа должна быть готова (3-5 участников)
        """
        if self.status != RequestStatus.DRAFT:
            raise ValueError("Нельзя назначить группу для заявки в статусе не DRAFT")
        
        if not group.is_ready():
            raise ValueError(f"Группа {group.group_id} не готова (нужно 3-5 участников)")
        
        self.assigned_group = group
        
        event = GroupAssignedToRequest(
            request_id=self.request_id,
            group_id=group.group_id,
            occurred_at=datetime.now()
        )
        self._events.append(event)
    
    def activate(self) -> None:
        """
        Активировать заявку (начать операцию)
        
        Инварианты:
        - Должна быть назначена группа
        - Статус должен быть DRAFT
        """
        if self.assigned_group is None:
            raise ValueError("Нельзя активировать заявку без назначенной группы")
        
        if self.status != RequestStatus.DRAFT:
            raise ValueError(f"Нельзя активировать заявку в статусе {self.status.value}")
        
        self.status = RequestStatus.ACTIVE
        self.activated_at = datetime.now()
        
        event = RequestActivated(
            request_id=self.request_id,
            group_id=self.assigned_group.group_id,
            zone_name=self.zone.name,
            occurred_at=self.activated_at
        )
        self._events.append(event)
    
    def change_zone(self, new_zone: Zone) -> None:
        """
        Изменить зону поиска
        
        Инварианты:
        - Нельзя изменить для завершённой заявки
        """
        if self.status == RequestStatus.COMPLETED:
            raise ValueError("Нельзя изменить зону для завершённой заявки")
        
        old_zone_name = self.zone.name
        self.zone = new_zone
        
        event = RequestZoneChanged(
            request_id=self.request_id,
            old_zone=old_zone_name,
            new_zone=new_zone.name,
            occurred_at=datetime.now()
        )
        self._events.append(event)
    
    def complete(self, outcome: str) -> None:
        """
        Завершить операцию
        
        Args:
            outcome: "SUCCESS" или "ABORTED"
        """
        if outcome not in ("SUCCESS", "ABORTED"):
            raise ValueError("Outcome должен быть SUCCESS или ABORTED")
        
        if self.status == RequestStatus.COMPLETED:
            raise ValueError("Заявка уже завершена")
        
        self.status = RequestStatus.COMPLETED
        self.completed_at = datetime.now()
        
        event = RequestCompleted(
            request_id=self.request_id,
            outcome=outcome,
            occurred_at=self.completed_at
        )
        self._events.append(event)
    
    def get_events(self) -> List:
        """Получить доменные события"""
        return self._events.copy()
    
    def clear_events(self) -> None:
        """Очистить события после публикации"""
        self._events.clear()
    
    def __eq__(self, other):
        """Сравнение по ID (идентичность)"""
        if not isinstance(other, Request):
            return False
        return self.request_id == other.request_id
    
    def __hash__(self):
        return hash(self.request_id)
