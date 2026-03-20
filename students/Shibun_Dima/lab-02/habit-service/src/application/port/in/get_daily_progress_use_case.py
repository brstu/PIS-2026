from abc import ABC, abstractmethod

class GetDailyProgressUseCase(ABC):
    """
    Входящий порт: получение прогресса за текущий день.
    """

    @abstractmethod
    def get_progress(self, user_id: str) -> dict:
        """
        Возвращает прогресс пользователя за день.
        :param user_id: идентификатор пользователя
        :return: словарь с прогрессом (например: {"total": 1200, "goal": 2000})
        """
        pass
