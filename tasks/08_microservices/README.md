# Лабораторная работа №8. Microservices (Микросервисы)

**Дисциплина:** Проектирование интернет-систем  
**Тема:** Разделение на bounded contexts, Event Bus, API Gateway

---

## Цель работы

Разбить монолит на **микросервисы** по bounded contexts:
- **Request Service** — управление заявками
- **Group Service** — управление группами
- **Notification Service** — отправка уведомлений

---

## Результаты обучения

- **Определять** bounded contexts
- **Реализовывать** асинхронную коммуникацию (RabbitMQ/Kafka)
- **Настраивать** API Gateway
- **Обеспечивать** отказоустойчивость (Circuit Breaker)

---

## Задание

### Часть 1. Request Service

**Ответственность:**
- Создание заявок
- Назначение групп
- Управление статусом

📖 **Пример:** [examples/services/request-service/](examples/services/request-service/)

---

### Часть 2. Group Service

**Ответственность:**
- CRUD групп
- Управление участниками
- Проверка готовности

📖 **Пример:** [examples/services/group-service/](examples/services/group-service/)

---

### Часть 3. Event Bus (RabbitMQ)

**События:**
- `GroupAssignedToRequest` → Notification Service
- `RequestActivated` → Notification Service

📖 **Пример:** [examples/services/request-service/infrastructure/event_bus/rabbitmq_publisher.py](examples/services/request-service/infrastructure/event_bus/rabbitmq_publisher.py)

---

### Часть 4. API Gateway

**Маршрутизация:**
- `/requests/**` → Request Service
- `/groups/**` → Group Service

📖 **Пример:** [examples/api-gateway/nginx.conf](examples/api-gateway/nginx.conf)

---

<!-- START:artifacts -->
## Структура отчёта

📄 **[Макет отчёта →](Макет_отчета.md)**

```
lab-08/
├── Отчет.md
├── services/
│   ├── request_service/
│   ├── group_service/
│   └── notification_service/
├── event_bus/
│   └── rabbitmq_config.py
└── docker-compose.yml
```
<!-- END:artifacts -->

<!-- START:criteria -->
## Критерии оценки

| Критерий | Баллы | Требования |
|----------|-------|------------|
| Request Service: bounded context | 20 | Изолированная БД |
| Group Service: CRUD | 15 | REST API |
| Event Bus: асинхронная коммуникация | 25 | RabbitMQ/Kafka |
| API Gateway: маршрутизация | 15 | Nginx/Kong |
| Отказоустойчивость: Circuit Breaker | 15 | Retry, fallback |
| Docker Compose: оркестрация | 5 | Все сервисы |
| Качество документации | 5 | Диаграммы C4 |
| **ИТОГО** | **100** | |
<!-- END:criteria -->

<!-- START:bonuses -->
## Бонусы (+ до 15)

* **Service Mesh (Istio)** (+6) — Observability
* **Saga Pattern** (+5) — Распределённые транзакции
* **Tracing (Jaeger)** (+4) — Отслеживание запросов
<!-- END:bonuses -->

## Контрольные вопросы

1. **Что такое bounded context?**
2. **Почему микросервисы не должны делить БД?**
3. **В чём проблема распределённых транзакций?**
4. **Зачем нужен Circuit Breaker?**

---

## Срок сдачи

**Неделя 16-17 семестра**
