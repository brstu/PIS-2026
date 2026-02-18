"""
Domain Layer: RequestStatus (Статус заявки)

Enum для статусов жизненного цикла заявки.

Жизненный цикл:
DRAFT → ACTIVE → COMPLETED
"""
from enum import Enum


class RequestStatus(Enum):
    """Статусы заявки"""
    
    DRAFT = "Черновик"
    ACTIVE = "Активна"
    COMPLETED = "Завершена"
    
    def can_transition_to(self, target: 'RequestStatus') -> bool:
        """
        Можно ли перейти в указанный статус
        
        Args:
            target: Целевой статус
            
        Returns:
            True если переход допустим
        """
        if self == RequestStatus.DRAFT:
            return target == RequestStatus.ACTIVE
        elif self == RequestStatus.ACTIVE:
            return target == RequestStatus.COMPLETED
        elif self == RequestStatus.COMPLETED:
            return False  # Из завершённой заявки никуда нельзя перейти
        return False
    
    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return f"RequestStatus.{self.name}"
