"""
Domain Layer: Zone (Зона поиска)

Value Object для зон поиска.

Четыре основные зоны:
- NORTH (Север)
- SOUTH (Юг)
- EAST (Восток)
- WEST (Запад)

Свойства Value Object:
- Immutable (неизменяемый)
- Equality by value (сравнение по значению)
"""
from enum import Enum
from typing import Any


class Zone(Enum):
    """Value Object: Зона поиска"""
    
    NORTH = ("NORTH", "Северная зона")
    SOUTH = ("SOUTH", "Южная зона")
    EAST = ("EAST", "Восточная зона")
    WEST = ("WEST", "Западная зона")
    
    def __init__(self, name: str, display_name: str):
        self._name_value = name
        self._display_name = display_name
    
    @property
    def display_name(self) -> str:
        return self._display_name
    
    @classmethod
    def from_string(cls, name: str) -> 'Zone':
        """
        Создать зону по имени
        
        Args:
            name: Имя зоны (NORTH/SOUTH/EAST/WEST)
            
        Returns:
            Zone объект
            
        Raises:
            ValueError: если имя неизвестно
        """
        name_upper = name.upper()
        for zone in cls:
            if zone._name_value == name_upper:
                return zone
        
        raise ValueError(
            f"Неизвестная зона: {name}. "
            f"Допустимые: NORTH, SOUTH, EAST, WEST"
        )
    
    def __str__(self) -> str:
        return f"{self._display_name} ({self._name_value})"
    
    def __repr__(self) -> str:
        return f"Zone.{self.name}"
    
    # Value Object: сравнение по значению (автоматически в Enum)
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Zone):
            return False
        return self._name_value == other._name_value
    
    def __hash__(self) -> int:
        return hash(self._name_value)
