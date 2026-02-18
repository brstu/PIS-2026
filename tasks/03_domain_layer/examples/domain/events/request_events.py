"""
Domain Events: События для Request

Доменные события регистрируются при изменении состояния агрегата Request
Предметная область: ПСО «Юго-Запад»
"""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class GroupAssignedToRequest:
    """Событие: Группа назначена на заявку"""
    request_id: str
    group_id: str
    occurred_at: datetime


@dataclass(frozen=True)
class RequestActivated:
    """Событие: Заявка активирована (операция началась)"""
    request_id: str
    group_id: str
    zone_name: str
    occurred_at: datetime


@dataclass(frozen=True)
class RequestZoneChanged:
    """Событие: Зона поиска изменена"""
    request_id: str
    old_zone: str
    new_zone: str
    occurred_at: datetime


@dataclass(frozen=True)
class RequestCompleted:
    """Событие: Операция завершена"""
    request_id: str
    outcome: str  # "SUCCESS", "ABORTED"
    occurred_at: datetime
