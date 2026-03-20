class HabitService:
    """
    Application Service.
    Реализация use-cases для управления привычкой «Пить воду».
    """

    def __init__(self, water_repository, reminder_service):
        self.water_repository = water_repository
        self.reminder_service = reminder_service

    def log_water(self, command):
        """
        TODO: реализовать в ЛР-4
        1. Создать WaterEntry (domain)
        2. Сохранить через repository
        3. Вернуть результат
        """
        raise NotImplementedError("Будет реализовано в Lab #4")

    def get_progress(self, user_id: str):
        """
        TODO: реализовать в ЛР-4
        """
        raise NotImplementedError("Будет реализовано в Lab #4")
