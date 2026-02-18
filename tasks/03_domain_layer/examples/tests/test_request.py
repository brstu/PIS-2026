"""
Юнит-тесты для Request (Aggregate Root)

Проверка инвариантов и доменных событий
"""
import pytest
from datetime import datetime
from domain.models.request import Request
from domain.models.group import Group
from domain.models.zone import Zone
from domain.events.request_events import GroupAssignedToRequest, RequestActivated


class TestRequestInvariants:
    """Тесты инвариантов агрегата Request"""
    
    def test_should_not_assign_group_if_not_draft(self):
        """Нельзя назначить группу для активной заявки"""
        # Arrange
        zone = Zone("North", (52.0, 52.5, 23.5, 24.0))
        request = Request("REQ-2024-0001", "COORD-1", zone)
        
        group = Group("G-01", "LEADER-1")
        for i in range(3):
            group.add_member(f"VOL-{i}")
        group.mark_ready()
        
        request.assign_group(group)
        request.activate()
        
        # Act & Assert
        new_group = Group("G-02", "LEADER-2")
        with pytest.raises(ValueError, match="Нельзя назначить группу"):
            request.assign_group(new_group)
    
    def test_should_not_activate_without_group(self):
        """Нельзя активировать заявку без группы"""
        # Arrange
        zone = Zone("North", (52.0, 52.5, 23.5, 24.0))
        request = Request("REQ-2024-0001", "COORD-1", zone)
        
        # Act & Assert
        with pytest.raises(ValueError, match="без назначенной группы"):
            request.activate()
    
    def test_should_register_event_when_group_assigned(self):
        """Должно регистрироваться событие GroupAssignedToRequest"""
        # Arrange
        zone = Zone("North", (52.0, 52.5, 23.5, 24.0))
        request = Request("REQ-2024-0001", "COORD-1", zone)
        
        group = Group("G-01", "LEADER-1")
        for i in range(3):
            group.add_member(f"VOL-{i}")
        
        # Act
        request.assign_group(group)
        
        # Assert
        events = request.get_events()
        assert len(events) == 1
        assert isinstance(events[0], GroupAssignedToRequest)
        assert events[0].request_id == "REQ-2024-0001"
        assert events[0].group_id == "G-01"
    
    def test_should_not_change_zone_for_completed_request(self):
        """Нельзя изменить зону для завершённой заявки"""
        # Arrange
        zone = Zone("North", (52.0, 52.5, 23.5, 24.0))
        request = Request("REQ-2024-0001", "COORD-1", zone)
        
        group = Group("G-01", "LEADER-1")
        for i in range(3):
            group.add_member(f"VOL-{i}")
        group.mark_ready()
        
        request.assign_group(group)
        request.activate()
        request.complete("SUCCESS")
        
        # Act & Assert
        new_zone = Zone("South", (51.5, 52.0, 23.5, 24.0))
        with pytest.raises(ValueError, match="завершённой заявки"):
            request.change_zone(new_zone)


class TestRequestEvents:
    """Тесты доменных событий"""
    
    def test_should_clear_events_after_publishing(self):
        """События должны очищаться после публикации"""
        # Arrange
        zone = Zone("North", (52.0, 52.5, 23.5, 24.0))
        request = Request("REQ-2024-0001", "COORD-1", zone)
        
        group = Group("G-01", "LEADER-1")
        for i in range(3):
            group.add_member(f"VOL-{i}")
        
        request.assign_group(group)
        
        # Act
        events = request.get_events()
        assert len(events) == 1
        
        request.clear_events()
        
        # Assert
        assert len(request.get_events()) == 0
