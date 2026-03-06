# Python Examples for Lab #2

Примеры реализации гексагональной архитектуры на Python для ПСО «Юго-Запад».

## Структура

```
src_python/
├── domain/                    # Domain Layer
│   ├── request.py
│   ├── group.py
│   ├── zone.py
│   └── request_status.py
├── application/               # Application Layer
│   ├── port/
│   │   ├── in/
│   │   │   └── create_request_use_case.py
│   │   └── out/
│   │       ├── request_repository.py
│   │       └── notification_service.py
│   └── service/
│       └── request_service.py
├── infrastructure/             # Infrastructure Layer
│   ├── adapter/
│   │   ├── in/
│   │   │   └── request_controller.py
│   │   └── out/
│   │       ├── in_memory_request_repository.py
│   │       └── mock_sms_service.py
│   └── config/
│       └── dependency_injection.py
├── main.py                     # FastAPI приложение
├── example_cli.py              # CLI пример
└── requirements.txt            # Зависимости
```

## Установка

```bash
# Создать виртуальное окружение
python -m venv venv

# Активировать (Windows)
venv\Scripts\activate

# Активировать (Linux/Mac)
source venv/bin/activate

# Установить зависимости
pip install -r requirements.txt
```

## Запуск

### Вариант 1: CLI (без REST API)

```bash
python example_cli.py
```

Вывод:

```
============================================================
Request Service - ПСО «Юго-Запад»
Пример использования гексагон альной архитектуры
============================================================

📋 Создание заявки...
   Координатор: coordinator-001
   Зона: NORTH
   Волонтёры: vol-123, vol-456, vol-789

✅ [Repository] Сохранена заявка: REQ-2024-0042
📱 [SMS] Кому: +375-29-XXX-0123
   Сообщение: Вы назначены в группу G-03 для поиска в зоне Северная зона

📱 [SMS] Кому: +375-29-XXX-0456
   Сообщение: Вы назначены в группу G-03 для поиска в зоне Северная зона

📱 [SMS] Кому: +375-29-XXX-0789
   Сообщение: Вы назначены в группу G-03 для поиска в зоне Северная зона

============================================================
✅ Заявка успешно создана!
   ID: REQ-2024-0042
============================================================
```

### Вариант 2: REST API (FastAPI)

```bash
python main.py
```

Откроется на http://localhost:8000

**Документация API:** http://localhost:8000/docs

**Создать заявку:**

```bash
curl -X POST http://localhost:8000/api/requests \
  -H "Content-Type: application/json" \
  -d '{
    "coordinator_id": "coordinator-001",
    "zone": "NORTH",
    "volunteer_ids": ["vol-123", "vol-456", "vol-789"]
  }'
```

Ответ:

```json
{
  "request_id": "REQ-2024-0042"
}
```

## Ключевые концепции

### 1. Dependency Inversion

`RequestService` зависит от **интерфейсов** (портов), а не от конкретных адаптеров:

```python
# RequestService не знает про InMemoryRepository!
class RequestService:
    def __init__(
        self,
        repository: RequestRepository,        # Интерфейс!
        notifications: NotificationService    # Интерфейс!
    ):
        self._repository = repository
        self._notifications = notifications
```

### 2. Замена адаптеров

В `dependency_injection.py` можно заменить реализацию:

```python
# Было:
self._repository = InMemoryRequestRepository()

# Стало (в будущем):
self._repository = PostgreSQLRequestRepository()
```

`RequestService` не изменится!

### 3. Тестируемость

```python
import pytest
from unittest.mock import Mock

def test_create_request():
    # Моки адаптеров
    mock_repo = Mock(spec=RequestRepository)
    mock_sms = Mock(spec=NotificationService)

    # Сервис с моками
    service = RequestService(mock_repo, mock_sms)

    # Тест без реальной БД и SMS
    command = CreateRequestCommand(...)
    request_id = service.create_request(command)

    # Проверки
    mock_repo.save.assert_called_once()
    assert mock_sms.send_sms.call_count == 3
```

## Связь с Java примером

| Python | Java | Описание |
|--------|------|----------|
| `request.py` | `Request.java` | Domain entity |
| `abc.ABC` | `interface` | Определение портов |
| `@dataclass` | `record / class` | DTO |
| FastAPI | Spring Boot | REST framework |
| `Mock` (unittest) | Mockito | Тестирование |

## Дополнительно

Python версия подчёркивает те же принципы гексагональной архитектуры, что и Java:
- **Изоляция домена** от инфраструктуры
- **Dependency Inversion** через интерфейсы (ABC)
- **Тестируемость** через замену адаптеров
- **Гибкость** в выборе технологий (FastAPI, Flask, Django...)
