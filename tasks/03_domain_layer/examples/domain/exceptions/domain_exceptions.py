"""
Domain Exceptions: Доменные исключения

Исключения для бизнес-логики Request Service
Предметная область: ПСО «Юго-Запад»
"""


class DomainException(Exception):
    """Базовый класс для доменных исключений"""
    pass


class InvalidRequestStateException(DomainException):
    """Исключение: Недопустимое состояние заявки"""
    pass


class InvalidGroupSizeException(DomainException):
    """Исключение: Некорректный размер группы"""
    pass
