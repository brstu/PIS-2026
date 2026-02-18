"""
RequestDto: Read-модель для заявки

Упрощённая модель для чтения (без доменных методов)
Предметная область: ПСО «Юго-Запад»
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class RequestDto:
    """
    DTO для чтения заявки
    
    Отличие от доменной модели Request:
    - Плоская структура (без вложенных объектов)
    - Только данные (без методов)
    - Оптимизирована для передачи по сети
    """
    request_id: str
    coordinator_id: str
    status: str  # "DRAFT", "ACTIVE", "COMPLETED"
    zone_name: str
    zone_bounds: tuple[float, float, float, float]
    assigned_group_id: Optional[str] = None
    created_at: Optional[datetime] = None
    activated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
