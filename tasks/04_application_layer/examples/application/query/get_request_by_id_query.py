"""
GetRequestByIdQuery: Запрос заявки по ID

Не изменяет состояние системы
Предметная область: ПСО «Юго-Запад»
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class GetRequestByIdQuery:
    """
    Запрос: Получить заявку по ID
    
    Поля:
    - request_id: ID заявки (REQ-2024-NNNN)
    """
    request_id: str
    
    def __post_init__(self):
        if not self.request_id:
            raise ValueError("request_id обязателен")
