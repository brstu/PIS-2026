"""
Database Configuration: SQLAlchemy Session Management

Предметная область: ПСО «Юго-Запад»
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import os

# Database URL из переменной окружения
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/request_service")

# Engine: Connection Pool
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True  # Проверка соединения перед использованием
)

# SessionLocal: Factory для создания сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session() -> Session:
    """
    Dependency Injection для FastAPI
    
    Использование:
        @app.get("/requests/{id}")
        def get_request(id: str, db: Session = Depends(get_session)):
            ...
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@contextmanager
def session_scope():
    """
    Context Manager для ручного управления транзакциями
    
    Использование:
        with session_scope() as session:
            repo = RequestRepositoryImpl(session)
            repo.save(request)
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
