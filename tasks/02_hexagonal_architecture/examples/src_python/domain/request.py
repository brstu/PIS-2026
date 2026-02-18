"""
Domain Layer: Request (Заявка)

Агрегат для управления заявками на поисково-спасательные операции.
Предметная область: ПСО «Юго-Запад»

Business Rules:
- ID формата: REQ-YYYY-NNNN
- Создаётся в статусе DRAFT
- Группа должна содержать 3-5 участников
- После формирования группы → статус ACTIVE
"""
from datetime import datetime
from typing import Optional
import random

from .group import Group
from .zone import Zone
from .request_status import RequestStatus


class Request:
    """Агрегат: Заявка на поисково-спасательную операцию"""
    
    def __init__(self, coordinator_id: str, zone: Zone):
        """
        Создать новую заявку
        
        Args:
            coordinator_id: ID координатора
            zone: Зона поиска
        """
        self._id = self._generate_request_id()
        self._coordinator_id = coordinator_id
        self._zone = zone
        self._group: Optional[Group] = None
        self._status = RequestStatus.DRAFT
        self._created_at = datetime.now()
    
    def assign_group(self, group: Group) -> None:
        """
        Сформировать поисковую группу
        
        Args:
            group: Группа участников
            
        Raises:
            ValueError: если группа уже сформирована или размер недопустим
        """
        if self._status != RequestStatus.DRAFT:
            raise ValueError(
                f"Нельзя изменить группу для заявки в статусе: {self._status.value}"
            )
        
        member_count = group.member_count
        if member_count < 3 or member_count > 5:
            raise ValueError(
                f"Размер группы должен быть от 3 до 5 участников, текущий: {member_count}"
            )
        
        self._group = group
    
    def activate(self) -> None:
        """
        Активировать заявку (перевести в работу)
        
        Raises:
            ValueError: если группа не сформирована
        """
        if self._group is None:
            raise ValueError(
                "Нельзя активировать заявку без сформированной группы"
            )
        
        if self._status != RequestStatus.DRAFT:
            raise ValueError(
                f"Заявка уже имеет статус: {self._status.value}"
            )
        
        self._status = RequestStatus.ACTIVE
    
    def complete(self) -> None:
        """Завершить поисковую операцию"""
        if self._status != RequestStatus.ACTIVE:
            raise ValueError(
                f"Нельзя завершить заявку в статусе: {self._status.value}"
            )
        
        self._status = RequestStatus.COMPLETED
    
    def change_zone(self, new_zone: Zone) -> None:
        """
        Изменить зону поиска
        
        Args:
            new_zone: Новая зона
            
        Raises:
            ValueError: если заявка уже завершена
        """
        if self._status == RequestStatus.COMPLETED:
            raise ValueError(
                "Нельзя изменить зону для завершённой заявки"
            )
        self._zone = new_zone
    
    @staticmethod
    def _generate_request_id() -> str:
        """Генерация ID заявки формата REQ-YYYY-NNNN"""
        year = datetime.now().year
        random_num = random.randint(0, 9999)
        return f"REQ-{year}-{random_num:04d}"
    
    # Properties
    
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def coordinator_id(self) -> str:
        return self._coordinator_id
    
    @property
    def zone(self) -> Zone:
        return self._zone
    
    @property
    def group(self) -> Optional[Group]:
        return self._group
    
    @property
    def status(self) -> RequestStatus:
        return self._status
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def has_group(self) -> bool:
        return self._group is not None
    
    def __str__(self) -> str:
        return (
            f"Request(id={self._id}, coordinator={self._coordinator_id}, "
            f"zone={self._zone.name}, status={self._status.value}, "
            f"has_group={self.has_group})"
        )
    
    def __repr__(self) -> str:
        return self.__str__()
