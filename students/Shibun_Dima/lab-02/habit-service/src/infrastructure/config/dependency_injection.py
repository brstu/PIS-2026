from application.service.habit_service import HabitService
from infrastructure.adapter.out.in_memory_water_repository import InMemoryWaterRepository


class DependencyContainer:
    """
    Конфигурация DI: связывание портов и адаптеров.
    Здесь создаются реализации исходящих портов и передаются в сервис.
    """

    def __init__(self):
        # --- Исходящие адаптеры ---
        self.water_repository = InMemoryWaterRepository()
        self.reminder_service = None  # TODO: добавить Email/SMS сервис в ЛР-4/5

        # --- Application Service ---
        self.habit_service = HabitService(
            water_repository=self.water_repository,
            reminder_service=self.reminder_service
        )

    def get_habit_service(self):
        """
        Возвращает готовый HabitService со всеми зависимостями.
        """
        return self.habit_service
