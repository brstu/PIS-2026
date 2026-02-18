"""
CreateRequestHandler: Обработчик команды создания заявки

Предметная область: ПСО «Юго-Запад»
"""
from datetime import datetime
from application.command.create_request_command import CreateRequestCommand
from domain.models.request import Request
from domain.models.zone import Zone


class CreateRequestHandler:
    """
    Handler: Создать новую заявку
    
    Шаги:
    1. Валидация команды
    2. Создание агрегата Request
    3. Сохранение через Repository
    4. Публикация событий (если нужно)
    5. Возврат ID заявки
    """
    
    def __init__(self, request_repository, event_publisher=None):
        self.request_repository = request_repository
        self.event_publisher = event_publisher
    
    def handle(self, command: CreateRequestCommand) -> str:
        """
        Обработать команду CreateRequest
        
        Returns:
            ID созданной заявки (REQ-2024-NNNN)
        """
        # 1. Валидация (примитивы уже проверены в __post_init__)
        self._validate_zone_bounds(command.zone_bounds)
        
        # 2. Генерация ID
        request_id = self._generate_request_id()
        
        # 3. Создание Zone
        zone = Zone(command.zone_name, command.zone_bounds)
        
        # 4. Создание агрегата Request
        request = Request(
            request_id=request_id,
            coordinator_id=command.coordinator_id,
            zone=zone
        )
        
        # 5. Сохранение
        self.request_repository.save(request)
        
        # 6. Публикация доменных событий (если есть)
        if self.event_publisher:
            for event in request.get_events():
                self.event_publisher.publish(event)
            request.clear_events()
        
        return request_id
    
    def _validate_zone_bounds(self, bounds):
        """Валидация границ зоны"""
        lat_min, lat_max, lon_min, lon_max = bounds
        if lat_min >= lat_max or lon_min >= lon_max:
            raise ValueError("Некорректные границы зоны")
    
    def _generate_request_id(self) -> str:
        """Генерация уникального ID заявки"""
        year = datetime.now().year
        # В реальности: запрос к БД для получения sequence
        counter = 1
        return f"REQ-{year}-{counter:04d}"
