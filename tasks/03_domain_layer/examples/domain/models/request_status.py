"""
Domain Layer: RequestStatus (Статус заявки)

Value Object (Enum): Статус поисково-спасательной заявки
Предметная область: ПСО «Юго-Запад»
"""
from enum import Enum


class RequestStatus(Enum):
    """
    Статусы жизненного цикла заявки
    
    Transitions:
        DRAFT → ACTIVE → COMPLETED
        DRAFT → CANCELLED
        ACTIVE → CANCELLED
    """
    
    DRAFT = "DRAFT"           # Черновик (группа ещё не назначена)
    ACTIVE = "ACTIVE"         # Активная (операция в процессе)
    COMPLETED = "COMPLETED"   # Завершена успешно
    CANCELLED = "CANCELLED"   # Отменена
    
    def __str__(self) -> str:
        return self.value
    
    def can_transition_to(self, new_status: 'RequestStatus') -> bool:
        """
        Проверить, возможен ли переход в новый статус
        
        Args:
            new_status: Целевой статус
        
        Returns:
            True если переход допустим
        """
        valid_transitions = {
            RequestStatus.DRAFT: {RequestStatus.ACTIVE, RequestStatus.CANCELLED},
            RequestStatus.ACTIVE: {RequestStatus.COMPLETED, RequestStatus.CANCELLED},
            RequestStatus.COMPLETED: set(),  # Финальный статус
            RequestStatus.CANCELLED: set(),  # Финальный статус
        }
        
        return new_status in valid_transitions.get(self, set())
    
    @property
    def is_final(self) -> bool:
        """Проверка финального статуса (нельзя изменить)"""
        return self in {RequestStatus.COMPLETED, RequestStatus.CANCELLED}
    
    @property
    def is_active(self) -> bool:
        """Проверка активной заявки (операция в процессе)"""
        return self == RequestStatus.ACTIVE
    
    @property
    def display_name_ru(self) -> str:
        """Название статуса на русском для UI"""
        names = {
            RequestStatus.DRAFT: "Черновик",
            RequestStatus.ACTIVE: "В работе",
            RequestStatus.COMPLETED: "Завершена",
            RequestStatus.CANCELLED: "Отменена",
        }
        return names[self]
