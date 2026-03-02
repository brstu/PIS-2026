"""
CLI Example: Демонстрация работы без REST API

Простой пример использования сервиса через командную строку.
"""
from application.port.in import CreateRequestCommand
from infrastructure.config import get_container


def main():
    """Главная функция CLI примера"""
    print("=" * 60)
    print("Request Service - ПСО «Юго-Запад»")
    print("Пример использования гексагональной архитектуры")
    print("=" * 60)
    print()

    # Получить DI-контейнер
    container = get_container()
    service = container.get_request_service()

    # Создать команду
    command = CreateRequestCommand(
        coordinator_id="coordinator-001",
        zone="NORTH",
        volunteer_ids=["vol-123", "vol-456", "vol-789"]
    )

    print("📋 Создание заявки...")
    print(f"   Координатор: {command.coordinator_id}")
    print(f"   Зона: {command.zone}")
    print(f"   Волонтёры: {', '.join(command.volunteer_ids)}")
    print()

    # Вызвать use-case
    try:
        request_id = service.create_request(command)

        print("=" * 60)
        print(f"✅ Заявка успешно создана!")
        print(f"   ID: {request_id}")
        print("=" * 60)

    except ValueError as e:
        print(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    main()
