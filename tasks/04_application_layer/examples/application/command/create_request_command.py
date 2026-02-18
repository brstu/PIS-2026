"""
CreateRequestCommand: Команда создания заявки

Иммутабельный DTO без бизнес-логики
Предметная область: ПСО «Юго-Запад»
"""
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class CreateRequestCommand:
    """
    Команда: Создать новую заявку
    
    Поля:
    - coordinator_id: ID координатора
    - zone_name: Название зоны
    - zone_bounds: Границы зоны (lat_min, lat_max, lon_min, lon_max)
    """
    coordinator_id: str
    zone_name: str
    zone_bounds: Tuple[float, float, float, float]
    
    def __post_init__(self):
        """Базовая валидация примитивов"""
        if not self.coordinator_id:
            raise ValueError("coordinator_id обязателен")
        if not self.zone_name:
            raise ValueError("zone_name обязательно")
        if len(self.zone_bounds) != 4:
            raise ValueError("zone_bounds должно содержать 4 элемента")
