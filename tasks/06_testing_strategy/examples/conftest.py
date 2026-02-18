"""
Pytest Fixtures: Переиспользуемые компоненты для тестов

Shared fixtures для всех тестов
"""
import pytest
from unittest.mock import Mock
from datetime import datetime
from domain.models.request import Request
from domain.models.group import Group
from domain.models.zone import Zone


# === Domain Fixtures ===

@pytest.fixture
def sample_zone():
    """Fixture: Пример зоны поиска"""
    return Zone("North", (52.0, 52.5, 23.5, 24.0))


@pytest.fixture
def sample_group():
    """Fixture: Готовая группа (3 участника)"""
    group = Group("G-01", "LEADER-1")
    group.add_member("VOL-001")
    group.add_member("VOL-002")
    group.mark_ready()
    return group


@pytest.fixture
def sample_request(sample_zone):
    """Fixture: Пример заявки в статусе DRAFT"""
    return Request("REQ-2024-0001", "COORD-1", sample_zone)


@pytest.fixture
def active_request(sample_zone, sample_group):
    """Fixture: Активная заявка"""
    request = Request("REQ-2024-0001", "COORD-1", sample_zone)
    request.assign_group(sample_group)
    request.activate()
    return request


# === Mock Fixtures ===

@pytest.fixture
def mock_request_repository():
    """Fixture: Mock RequestRepository"""
    repo = Mock()
    repo.save = Mock()
    repo.find_by_id = Mock(return_value=None)
    repo.find_active_requests = Mock(return_value=[])
    return repo


@pytest.fixture
def mock_event_publisher():
    """Fixture: Mock Event Publisher"""
    publisher = Mock()
    publisher.publish = Mock()
    return publisher


# === Pytest Configuration ===

def pytest_configure(config):
    """Кастомная конфигурация pytest"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as an end-to-end test"
    )
