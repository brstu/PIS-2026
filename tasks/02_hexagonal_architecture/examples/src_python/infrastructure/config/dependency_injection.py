"""
Infrastructure Layer: Dependency Injection Configuration

Конфигурация Dependency Injection (DI).
Здесь создаются экземпляры адаптеров и сервисов.
"""
from fastapi import FastAPI

from application.port.out import RequestRepository, NotificationService
from application.service import RequestService
from infrastructure.adapter.out import InMemoryRequestRepository, MockSmsService
from infrastructure.adapter.in import RequestController


class DependencyContainer:
    """
    DI-контейнер: Управление зависимостями
    
    Создаёт и связывает все компоненты системы.
    """
    
    def __init__(self):
        """Инициализация контейнера"""
        # Создать исходящие адаптеры (реализации портов)
        self._repository: RequestRepository = InMemoryRequestRepository()
        self._notifications: NotificationService = MockSmsService()
        
        # Создать application service (инжектируем зависимости)
        self._request_service = RequestService(
            repository=self._repository,
            notifications=self._notifications
        )
    
    def get_request_service(self) -> RequestService:
        """Получить RequestService (use-case)"""
        return self._request_service
    
    def get_repository(self) -> RequestRepository:
        """Получить репозиторий"""
        return self._repository
    
    def configure_web_app(self, app: FastAPI) -> None:
        """
        Настроить FastAPI приложение
        
        Args:
            app: FastAPI приложение
        """
        # Создать входящий адаптер (REST API)
        RequestController(
            app=app,
            use_case=self._request_service
        )


# Глобальный экземпляр контейнера
_container: DependencyContainer | None = None


def get_container() -> DependencyContainer:
    """Получить глобальный DI-контейнер"""
    global _container
    if _container is None:
        _container = DependencyContainer()
    return _container


def reset_container() -> None:
    """Сбросить контейнер (для тестов)"""
    global _container
    _container = None
