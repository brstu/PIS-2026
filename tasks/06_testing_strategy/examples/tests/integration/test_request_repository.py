"""
Интеграционные тесты для RequestRepository

Проверка:
- Сохранение/загрузка агрегата из PostgreSQL
- Корректность ORM-маппинга
- Работа с реальной БД через testcontainers
"""
import pytest
from testcontainers.postgres import PostgresContainer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from infrastructure.adapter.out.request_repository_impl import RequestRepositoryImpl
from infrastructure.orm.models import Base, RequestORM
from domain.models.request import Request
from domain.models.zone import Zone
from domain.models.request_status import RequestStatus


@pytest.fixture(scope="module")
def postgres_container():
    """Fixture: PostgreSQL в Docker (testcontainers)"""
    with PostgresContainer("postgres:16-alpine") as postgres:
        yield postgres


@pytest.fixture
def db_session(postgres_container):
    """Fixture: SQLAlchemy Session с чистой БД"""
    # Создание engine
    engine = create_engine(postgres_container.get_connection_url())
    
    # Создание таблиц
    Base.metadata.create_all(engine)
    
    # Session factory
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    yield session
    
    # Cleanup
    session.rollback()
    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def repository(db_session):
    """Fixture: RequestRepository с реальной БД"""
    return RequestRepositoryImpl(db_session)


class TestRequestRepositorySave:
    """Тесты сохранения Request"""
    
    def test_should_save_new_request(self, repository, db_session):
        """Должен сохранить новую заявку"""
        # Arrange
        zone = Zone("North", (52.0, 52.5, 23.5, 24.0))
        request = Request("REQ-2024-0001", "COORD-1", zone)
        
        # Act
        repository.save(request)
        
        # Assert
        orm_request = db_session.query(RequestORM).filter_by(
            request_id="REQ-2024-0001"
        ).first()
        
        assert orm_request is not None
        assert orm_request.coordinator_id == "COORD-1"
        assert orm_request.status == "DRAFT"
        assert orm_request.zone.name == "North"
    
    def test_should_update_existing_request(self, repository, db_session):
        """Должен обновить существующую заявку"""
        # Arrange
        zone = Zone("North", (52.0, 52.5, 23.5, 24.0))
        request = Request("REQ-2024-0001", "COORD-1", zone)
        repository.save(request)
        
        # Изменение состояния
        new_zone = Zone("South", (51.5, 52.0, 23.5, 24.0))
        request.change_zone(new_zone)
        
        # Act
        repository.save(request)
        
        # Assert
        orm_request = db_session.query(RequestORM).filter_by(
            request_id="REQ-2024-0001"
        ).first()
        
        assert orm_request.zone.name == "South"
        assert orm_request.zone.lat_min == 51.5


class TestRequestRepositoryFind:
    """Тесты поиска Request"""
    
    def test_should_find_request_by_id(self, repository):
        """Должен найти заявку по ID"""
        # Arrange
        zone = Zone("North", (52.0, 52.5, 23.5, 24.0))
        request = Request("REQ-2024-0001", "COORD-1", zone)
        repository.save(request)
        
        # Act
        found = repository.find_by_id("REQ-2024-0001")
        
        # Assert
        assert found is not None
        assert found.request_id == "REQ-2024-0001"
        assert found.coordinator_id == "COORD-1"
        assert found.zone.name == "North"
    
    def test_should_return_none_for_nonexistent_id(self, repository):
        """Должен вернуть None для несуществующего ID"""
        # Act
        found = repository.find_by_id("REQ-9999-9999")
        
        # Assert
        assert found is None
    
    def test_should_find_active_requests(self, repository, db_session):
        """Должен найти все активные заявки"""
        # Arrange
        # Создаём 3 заявки: 2 активные, 1 draft
        zone = Zone("North", (52.0, 52.5, 23.5, 24.0))
        
        request1 = Request("REQ-2024-0001", "COORD-1", zone)
        repository.save(request1)
        
        request2 = Request("REQ-2024-0002", "COORD-1", zone)
        # Ручное изменение статуса (для теста)
        db_session.query(RequestORM).filter_by(
            request_id="REQ-2024-0002"
        ).update({"status": "ACTIVE"})
        db_session.commit()
        
        request3 = Request("REQ-2024-0003", "COORD-1", zone)
        db_session.query(RequestORM).filter_by(
            request_id="REQ-2024-0003"
        ).update({"status": "ACTIVE"})
        db_session.commit()
        
        # Act
        active_requests = repository.find_active_requests()
        
        # Assert
        assert len(active_requests) == 2
        assert all(r.status == RequestStatus.ACTIVE for r in active_requests)


class TestORMMapping:
    """Тесты корректности маппинга Domain ↔ ORM"""
    
    def test_domain_to_orm_mapping(self, repository, db_session):
        """Проверка преобразования Domain → ORM"""
        # Arrange
        zone = Zone("North", (52.0, 52.5, 23.5, 24.0))
        request = Request("REQ-2024-0001", "COORD-1", zone)
        
        # Act
        repository.save(request)
        
        # Assert
        orm_request = db_session.query(RequestORM).filter_by(
            request_id="REQ-2024-0001"
        ).first()
        
        assert orm_request.zone.lat_min == 52.0
        assert orm_request.zone.lat_max == 52.5
        assert orm_request.zone.lon_min == 23.5
        assert orm_request.zone.lon_max == 24.0
    
    def test_orm_to_domain_mapping(self, repository):
        """Проверка преобразования ORM → Domain"""
        # Arrange
        zone = Zone("North", (52.0, 52.5, 23.5, 24.0))
        request = Request("REQ-2024-0001", "COORD-1", zone)
        repository.save(request)
        
        # Act
        found = repository.find_by_id("REQ-2024-0001")
        
        # Assert
        assert found.zone.bounds == (52.0, 52.5, 23.5, 24.0)
        assert found.zone.area() > 0  # Value Object метод работает
