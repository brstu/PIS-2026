"""
AssignGroupToRequestCommand: Назначить группу на заявку

Предметная область: ПСО «Юго-Запад»
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class AssignGroupToRequestCommand:
    """
    Команда: Назначить группу на заявку
    
    Поля:
    - request_in: ID заявки (REQ-2024-NNNN)
    - group_id: ID группы (G-NN)
    """
    request_id: str
    group_id: str
    
    def __post_init__(self):
        if not self.request_id:
            raise ValueError("request_id обязателен")
        if not self.group_id:
            raise ValueError("group_id обязателен")
