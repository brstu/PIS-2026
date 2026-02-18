"""
Request Service - ПСО «Юго-Запад»

Реализация гексагональной архитектуры (Ports & Adapters)
для системы управления заявками поисково-спасательного отряда.

Основные слои:
- Domain Layer: Request, Group, Zone, RequestStatus
- Application Layer: CreateRequestUseCase, RequestService
- Infrastructure Layer: Adapters (REST, Repository, Notifications)
"""

__version__ = "1.0.0"
__author__ = "БрГТУ - Курс ПИС-2026"
