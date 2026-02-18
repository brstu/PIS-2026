"""
Юнит-тесты для Request (Aggregate Root)

Проверка:
- Инвариантов агрегата
- Регистрации доменных событий
- Переходов состояний
"""
import pytest
from datetime import datetime
from domain.models.request import Request
from domain.models.group import Group
from domain.models.zone import Zone
from domain.models.request_status import RequestStatus
from domain.events.request_events import (
    GroupAssignedToRequest,
    RequestActivated,
    RequestZoneChanged,
    RequestCompleted
)


class TestRequestInvariants:
    """Тесты бизнес-правил (инвариантов)"""
    
    def test_should_create_request_in_draft_status(self):
        """Новая заявка должна быть в статусе DRAFT"""
        # Arrange
        zone = Zone("North", (52.0, 52.5, 23.5, 24.0))
        
        # Act
        request = Request("REQ-2024-0001", "COORD-1", zone)
        
        # Assert
        assert request.status == RequestStatus.DRAFT
        assert request.assigned_group is None
        assert request.activated_at is None
    
    def test_should_not_activate_without_group(self):
        """Инвариант: Нельзя активировать заявку без группы"""
        # Arrange
        zone = Zone("North", (52.0, 52.5, 23.5, 24.0))
        request = Request("REQ-2024-0001", "COORD-1", zone)
        
        # Act & Assert
        with pytest.raises(ValueError, match="без назначенной группы"):
            request.activate()
    
    def test_should_not_assign_group_if_already_active(self):
        """Инвариант: Нельзя назначить группу для активной заявки"""
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
        with pytest.raises(ValueError, match="не DRAFT"):
            request.assign_group(new_group)
    
    def test_should_not_assign_unready_group(self):
        """Инвариант: Группа должна быть готова (3-5 участников)"""
        # Arrange
        zone = Zone("North", (52.0, 52.5, 23.5, 24.0))
        request = Request("REQ-2024-0001", "COORD-1", zone)
        
        group = Group("G-01", "LEADER-1")
        # Только 1 участник (лидер), нужно минимум 3
        
        # Act & Assert
        with pytest.raises(ValueError, match="не готова"):
            request.assign_group(group)
    
    def test_should_not_change_zone_for_completed_request(self):
        """Инвариант: Нельзя изменить зону для завершённой заявки"""
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


class TestRequestDomainEvents:
    """Тесты регистрации доменных событий"""
    
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
    
    def test_should_register_event_when_activated(self):
        """Должно регистрироваться событие RequestActivated"""
        # Arrange
        zone = Zone("North", (52.0, 52.5, 23.5, 24.0))
        request = Request("REQ-2024-0001", "COORD-1", zone)
        
        group = Group("G-01", "LEADER-1")
        for i in range(3):
            group.add_member(f"VOL-{i}")
        group.mark_ready()
        
        request.assign_group(group)
        
        # Act
        request.activate()
        
        # Assert
        events = request.get_events()
        activated_events = [e for e in events if isinstance(e, RequestActivated)]
        assert len(activated_events) == 1
        assert activated_events[0].zone_name == "North"
    
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


class TestRequestStateTransitions:
    """Тесты переходов между состояниями"""
    
    def test_state_transition_draft_to_active(self):
        """DRAFT → ACTIVE при активации"""
        # Arrange
        zone = Zone("North", (52.0, 52.5, 23.5, 24.0))
        request = Request("REQ-2024-0001", "COORD-1", zone)
        
        group = Group("G-01", "LEADER-1")
        for i in range(3):
            group.add_member(f"VOL-{i}")
        group.mark_ready()
        
        request.assign_group(group)
        
        # Act
        request.activate()
        
        # Assert
        assert request.status == RequestStatus.ACTIVE
        assert request.activated_at is not None
    
    def test_state_transition_active_to_completed(self):
        """ACTIVE → COMPLETED при завершении"""
        # Arrange
        zone = Zone("North", (52.0, 52.5, 23.5, 24.0))
        request = Request("REQ-2024-0001", "COORD-1", zone)
        
        group = Group("G-01", "LEADER-1")
        for i in range(3):
            group.add_member(f"VOL-{i}")
        group.mark_ready()
        
        request.assign_group(group)
        request.activate()
        
        # Act
        request.complete("SUCCESS")
        
        # Assert
        assert request.status == RequestStatus.COMPLETED
        assert request.completed_at is not None


class TestRequestEquality:
    """Тесты сравнения (identity-based)"""
    
    def test_requests_with_same_id_are_equal(self):
        """Заявки с одинаковым ID равны"""
        # Arrange
        zone1 = Zone("North", (52.0, 52.5, 23.5, 24.0))
        zone2 = Zone("South", (51.5, 52.0, 23.5, 24.0))
        
        request1 = Request("REQ-2024-0001", "COORD-1", zone1)
        request2 = Request("REQ-2024-0001", "COORD-2", zone2)
        
        # Assert
        assert request1 == request2
        assert hash(request1) == hash(request2)
    
    def test_requests_with_different_id_are_not_equal(self):
        """Заявки с разными ID не равны"""
        # Arrange
        zone = Zone("North", (52.0, 52.5, 23.5, 24.0))
        
        request1 = Request("REQ-2024-0001", "COORD-1", zone)
        request2 = Request("REQ-2024-0002", "COORD-1", zone)
        
        # Assert
        assert request1 != request2
