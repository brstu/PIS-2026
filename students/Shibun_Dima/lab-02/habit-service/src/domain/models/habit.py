class Habit:
    """
    Доменная модель: привычка «Пить воду».
    Минимальная версия для демонстрации.
    """

    def __init__(self, habit_id: str, user_id: str):
        self.id = habit_id
        self.user_id = user_id
        self.entries = []  # список выпитых объёмов (мл)

    def add_entry(self, amount_ml: int):
        """
        Добавляет запись о выпитом количестве воды.
        (Полная бизнес-логика будет в ЛР-3)
        """
        self.entries.append(amount_ml)
