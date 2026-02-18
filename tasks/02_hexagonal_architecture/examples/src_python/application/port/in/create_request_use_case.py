"""
Application Layer: CreateRequestUseCase (Входящий порт)

Интерфейс для создания заявки.
Клиенты системы вызывают этот интерфейс.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


@dataclass
class CreateRequestCommand:
    """DTO: Команда создания заявки"""
    coordinator_id: str
    zone: str  # "NORTH", "SOUTH", "EAST", "WEST"
    volunteer_ids: List[str]  # 3-5 участников


class CreateRequestUseCase(ABC):
    """Входящий порт: Создание заявки"""
    
    @abstractmethod
    def create_request(self, command: CreateRequestCommand) -> str:
        """
        Создать заявку на поисково-спасательную операцию
        
        Args:
            command: Команда с данными заявки
            
        Returns:
            ID созданной заявки (например, "REQ-2024-0042")
            
        Raises:
            ValueError: если данные некорректны
        """
        pass
