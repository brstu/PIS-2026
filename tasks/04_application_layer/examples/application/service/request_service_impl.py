"""
RequestServiceImpl: Фасад прикладного слоя

Предметная область: ПСО «Юго-Запад»
"""
from application.command.create_request_command import CreateRequestCommand
from application.command.handlers.create_request_handler import CreateRequestHandler
from application.query.get_request_by_id_query import GetRequestByIdQuery
from application.query.dto.request_dto import RequestDto
from application.query.handlers.get_request_by_id_handler import GetRequestByIdHandler


class RequestServiceImpl:
    """
    Application Service: фасад для Command/Query Handlers
    
    Зачем нужен:
    - Упрощает вызов прикладных операций (единая точка входа)
    - Инкапсулирует детали обработки команд и запросов
    - Удобен для использования в контроллерах
    """
    
    def __init__(
        self,
        create_request_handler: CreateRequestHandler,
        get_request_by_id_handler: GetRequestByIdHandler
    ):
        self.create_request_handler = create_request_handler
        self.get_request_by_id_handler = get_request_by_id_handler
    
    def create_request(self, command: CreateRequestCommand) -> str:
        """Создать заявку. Возвращает ID."""
        return self.create_request_handler.handle(command)
    
    def get_request_by_id(self, query: GetRequestByIdQuery) -> RequestDto:
        """Получить заявку по ID."""
        return self.get_request_by_id_handler.handle(query)
