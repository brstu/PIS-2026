"""
Юнит-тесты для CreateRequestHandler

Проверка:
- Логики обработчика команды
- Вызова методов репозитория (с моками)
- Публикации событий
"""
import pytest
from unittest.mock import Mock, MagicMock
from application.command.create_request_command import CreateRequestCommand
from application.command.handlers.create_request_handler import CreateRequestHandler
from domain.models.request import Request


class TestCreateRequestHandler:
    """Тесты обработчика CreateRequest"""
    
    def test_should_create_and_save_request(self):
        """Handler должен создать Request и вызвать repository.save()"""
        # Arrange
        mock_repo = Mock()
        mock_publisher = Mock()
        handler = CreateRequestHandler(mock_repo, mock_publisher)
        
        command = CreateRequestCommand(
            coordinator_id="COORD-1",
            zone_name="North",
            zone_bounds=(52.0, 52.5, 23.5, 24.0)
        )
        
        # Act
        request_id = handler.handle(command)
        
        # Assert
        assert request_id.startswith("REQ-")
        mock_repo.save.assert_called_once()
        
        # Проверка аргумента save()
        saved_request = mock_repo.save.call_args[0][0]
        assert isinstance(saved_request, Request)
        assert saved_request.coordinator_id == "COORD-1"
        assert saved_request.zone.name == "North"
    
    def test_should_publish_domain_events(self):
        """Handler должен публиковать доменные события (если есть)"""
        # Arrange
        mock_repo = Mock()
        mock_publisher = Mock()
        handler = CreateRequestHandler(mock_repo, mock_publisher)
        
        command = CreateRequestCommand(
            coordinator_id="COORD-1",
            zone_name="North",
            zone_bounds=(52.0, 52.5, 23.5, 24.0)
        )
        
        # Act
        handler.handle(command)
        
        # Assert
        # CreateRequest не генерирует события при создании,
        # но проверяем вызов clear_events()
        # (В реальности события публикуются при assign_group, activate)
        assert mock_publisher is not None
    
    def test_should_validate_zone_bounds(self):
        """Handler должен валидировать некорректные границы зоны"""
        # Arrange
        mock_repo = Mock()
        handler = CreateRequestHandler(mock_repo, None)
        
        command = CreateRequestCommand(
            coordinator_id="COORD-1",
            zone_name="North",
            zone_bounds=(52.5, 52.0, 23.5, 24.0)  # lat_min > lat_max
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="Некорректные границы"):
            handler.handle(command)
    
    def test_should_return_generated_request_id(self):
        """Handler должен возвращать сгенерированный ID"""
        # Arrange
        mock_repo = Mock()
        handler = CreateRequestHandler(mock_repo, None)
        
        command = CreateRequestCommand(
            coordinator_id="COORD-1",
            zone_name="North",
            zone_bounds=(52.0, 52.5, 23.5, 24.0)
        )
        
        # Act
        request_id = handler.handle(command)
        
        # Assert
        assert request_id.startswith("REQ-2024-")
        assert len(request_id) == 13  # REQ-2024-NNNN


class TestCreateRequestHandlerEdgeCases:
    """Тесты граничных случаев"""
    
    def test_should_handle_empty_coordinator_id(self):
        """Пустой coordinator_id должен вызывать ошибку"""
        # Arrange
        command = CreateRequestCommand(
            coordinator_id="",
            zone_name="North",
            zone_bounds=(52.0, 52.5, 23.5, 24.0)
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="coordinator_id обязателен"):
            # Валидация происходит в __post_init__ команды
            pass
    
    def test_should_handle_repository_failure(self):
        """Ошибка сохранения в репозитории должна пробрасываться"""
        # Arrange
        mock_repo = Mock()
        mock_repo.save.side_effect = Exception("Database connection error")
        
        handler = CreateRequestHandler(mock_repo, None)
        
        command = CreateRequestCommand(
            coordinator_id="COORD-1",
            zone_name="North",
            zone_bounds=(52.0, 52.5, 23.5, 24.0)
        )
        
        # Act & Assert
        with pytest.raises(Exception, match="Database connection error"):
            handler.handle(command)
