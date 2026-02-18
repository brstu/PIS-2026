"""
Application Layer: RequestService

Реализация use-case создания заявки.
Оркестрирует Domain Layer и вызывает внешние сервисы через порты.
"""
from application.port.in import CreateRequestUseCase, CreateRequestCommand
from application.port.out import RequestRepository, NotificationService
from domain import Request, Group, Zone


class RequestService(CreateRequestUseCase):
    """
    Application Service: Управление заявками
    
    Реализует входящие порты (use-cases) и использует исходящие порты
    для взаимодействия с внешним миром.
    """
    
    def __init__(
        self,
        repository: RequestRepository,
        notifications: NotificationService
    ):
        """
        Инициализация сервиса
        
        Args:
            repository: Репозиторий заявок (исходящий порт)
            notifications: Сервис уведомлений (исходящий порт)
        """
        self._repository = repository
        self._notifications = notifications
    
    def create_request(self, command: CreateRequestCommand) -> str:
        """
        Создать заявку на поисково-спасательную операцию
        
        Шаги:
        1. Создать агрегат Request (Domain Layer)
        2. Сформировать Group с участниками
        3. Назначить группу к заявке
        4. Активировать заявку
        5. Сохранить через репозиторий (исходящий порт)
        6. Отправить SMS уведомления (исходящий порт)
        7. Вернуть ID заявки
        
        Args:
            command: Команда создания заявки
            
        Returns:
            ID созданной заявки
            
        Raises:
            ValueError: если данные некорректны
        """
        # 1. Создать агрегат Request (Domain Layer)
        zone = Zone.from_string(command.zone)
        request = Request(
            coordinator_id=command.coordinator_id,
            zone=zone
        )
        
        # 2. Сформировать группу с участниками
        group_id = f"G-{len(command.volunteer_ids):02d}"
        group = Group(group_id)
        
        for volunteer_id in command.volunteer_ids:
            group.add_member(volunteer_id)
        
        # 3. Назначить группу к заявке
        request.assign_group(group)
        
        # 4. Активировать заявку
        request.activate()
        
        # 5. Сохранить через репозиторий (исходящий порт)
        self._repository.save(request)
        
        # 6. Отправить SMS уведомления участникам (исходящий порт)
        for volunteer_id in command.volunteer_ids:
            message = (
                f"Вы назначены в группу {group.id} "
                f"для поиска в зоне {zone.display_name}"
            )
            # В реальной системе здесь нужно получить номер телефона
            # через VolunteerRepository, но для примера упростим
            phone = f"+375-29-XXX-{volunteer_id[-4:]}"
            self._notifications.send_sms(phone, message)
        
        # 7. Вернуть ID заявки
        return request.id
