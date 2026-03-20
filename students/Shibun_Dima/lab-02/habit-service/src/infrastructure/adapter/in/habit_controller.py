# REST Controller (входящий адаптер)
# Здесь будет HTTP-эндпоинт
# Пока только демонстрационный метод

class HabitController:

    def __init__(self, habit_service):
        self.habit_service = habit_service

    def post_log_water(self, user_id: str, amount_ml: int):
        # TODO: подключить к реальному фреймворку (FastAPI/Flask)
        return {"status": "OK", "message": "Water logged"}
