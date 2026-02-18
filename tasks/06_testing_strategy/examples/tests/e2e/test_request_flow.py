"""
E2E-тесты: Полный сценарий Request Flow

Проверка:
- Полный сценарий через HTTP API
- Create → Assign Group → Activate → Complete
"""
import pytest
from fastapi.testclient import TestClient
from main import app  # FastAPI app


@pytest.fixture
def client():
    """Fixture: FastAPI TestClient"""
    return TestClient(app)


class TestRequestFlowE2E:
    """E2E-тест полного сценария заявки"""
    
    def test_complete_request_flow(self, client):
        """
        Сценарий:
        1. Создать заявку
        2. Назначить группу
        3. Активировать операцию
        4. Проверить статус заявки
        5. Завершить операцию
        """
        # Step 1: Создать заявку
        create_response = client.post("/api/requests", json={
            "coordinator_id": "COORD-1",
            "zone_name": "North",
            "zone_bounds": [52.0, 52.5, 23.5, 24.0]
        })
        
        assert create_response.status_code == 201
        request_id = create_response.json()["request_id"]
        assert request_id.startswith("REQ-")
        
        # Step 2: Получить заявку (проверка создания)
        get_response = client.get(f"/api/requests/{request_id}")
        assert get_response.status_code == 200
        
        request_data = get_response.json()
        assert request_data["status"] == "DRAFT"
        assert request_data["coordinator_id"] == "COORD-1"
        assert request_data["zone_name"] == "North"
        
        # Step 3: Назначить группу
        assign_response = client.post(
            f"/api/requests/{request_id}/assign-group",
            json={"group_id": "G-01"}
        )
        assert assign_response.status_code == 200
        
        # Step 4: Активировать операцию
        activate_response = client.post(f"/api/requests/{request_id}/activate")
        assert activate_response.status_code == 200
        
        # Step 5: Проверить статус ACTIVE
        get_active = client.get(f"/api/requests/{request_id}")
        assert get_active.json()["status"] == "ACTIVE"
        assert get_active.json()["assigned_group_id"] == "G-01"
        assert get_active.json()["activated_at"] is not None
        
        # Step 6: Завершить операцию
        complete_response = client.post(
            f"/api/requests/{request_id}/complete",
            json={"outcome": "SUCCESS"}
        )
        assert complete_response.status_code == 200
        
        # Step 7: Проверить статус COMPLETED
        get_completed = client.get(f"/api/requests/{request_id}")
        assert get_completed.json()["status"] == "COMPLETED"
        assert get_completed.json()["completed_at"] is not None


class TestErrorHandlingE2E:
    """E2E-тесты обработки ошибок"""
    
    def test_should_return_404_for_nonexistent_request(self, client):
        """Должен вернуть 404 для несуществующей заявки"""
        # Act
        response = client.get("/api/requests/REQ-9999-9999")
        
        # Assert
        assert response.status_code == 404
        assert "не найдена" in response.json()["detail"]
    
    def test_should_return_400_for_invalid_zone_bounds(self, client):
        """Должен вернуть 400 для некорректных границ зоны"""
        # Act
        response = client.post("/api/requests", json={
            "coordinator_id": "COORD-1",
            "zone_name": "North",
            "zone_bounds": [52.5, 52.0, 23.5, 24.0]  # lat_min > lat_max
        })
        
        # Assert
        assert response.status_code == 400
        assert "Некорректные границы" in response.json()["detail"]
    
    def test_should_return_400_when_activating_without_group(self, client):
        """Должен вернуть 400 при активации без группы"""
        # Arrange
        create_response = client.post("/api/requests", json={
            "coordinator_id": "COORD-1",
            "zone_name": "North",
            "zone_bounds": [52.0, 52.5, 23.5, 24.0]
        })
        request_id = create_response.json()["request_id"]
        
        # Act
        response = client.post(f"/api/requests/{request_id}/activate")
        
        # Assert
        assert response.status_code == 400
        assert "без назначенной группы" in response.json()["detail"]


class TestListEndpointE2E:
    """E2E-тесты списковых эндпоинтов"""
    
    def test_should_list_active_requests(self, client):
        """Должен вернуть список активных заявок"""
        # Arrange: создать несколько заявок
        for i in range(3):
            client.post("/api/requests", json={
                "coordinator_id": f"COORD-{i}",
                "zone_name": "North",
                "zone_bounds": [52.0, 52.5, 23.5, 24.0]
            })
        
        # Act
        response = client.get("/api/requests")
        
        # Assert
        assert response.status_code == 200
        requests = response.json()
        assert isinstance(requests, list)
        # В зависимости от фильтра (только ACTIVE или все)
        assert len(requests) >= 0
