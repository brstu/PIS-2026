from abc import ABC, abstractmethod

class LogWaterCommand:
    """
    DTO-команда для логирования воды.
    """
    def __init__(self, user_id: str, amount_ml: int):
        self.user_id = user_id
        self.amount_ml = amount_ml


class LogWaterUseCase(ABC):
    """
    Входящий порт: логирование выпитой воды.
    """

    @abstractmethod
    def log_water(self, command: LogWaterCommand) -> None:
        """
        Добавляет запись о выпитом количестве воды.
        :param command: данные для логирования
        """
        pass
