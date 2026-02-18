"""
ORM Models: SQLAlchemy модели для Request Service

Mapping Domain → Database Tables
Предметная область: ПСО «Юго-Запад»
"""
from sqlalchemy import Column, String, DateTime, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()


class RequestORM(Base):
    """
    ORM: Таблица requests
    
    Соответствует агрегату Request из Domain Layer
    """
    __tablename__ = "requests"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(String(50), unique=True, nullable=False, index=True)
    coordinator_id = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False, default="DRAFT")  # DRAFT, ACTIVE, COMPLETED
    assigned_group_id = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    activated_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationship: 1 Request → 1 Zone
    zone = relationship("ZoneORM", back_populates="request", uselist=False, cascade="all, delete-orphan")


class ZoneORM(Base):
    """
    ORM: Таблица zones
    
    Соответствует Value Object Zone
    """
    __tablename__ = "zones"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    request_id_fk = Column(Integer, ForeignKey("requests.id"), nullable=False)
    name = Column(String(50), nullable=False)
    lat_min = Column(Float, nullable=False)
    lat_max = Column(Float, nullable=False)
    lon_min = Column(Float, nullable=False)
    lon_max = Column(Float, nullable=False)
    
    # Relationship: Zone → Request
    request = relationship("RequestORM", back_populates="zone")


class GroupORM(Base):
    """
    ORM: Таблица groups
    
    Соответствует Entity Group
    """
    __tablename__ = "groups"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(String(50), unique=True, nullable=False, index=True)
    leader_id = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False, default="FORMING")  # FORMING, READY
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    
    # Relationship: 1 Group → many Members
    members = relationship("GroupMemberORM", back_populates="group", cascade="all, delete-orphan")


class GroupMemberORM(Base):
    """
    ORM: Таблица group_members
    
    Связь Group ↔ Volunteer
    """
    __tablename__ = "group_members"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id_fk = Column(Integer, ForeignKey("groups.id"), nullable=False)
    volunteer_id = Column(String(50), nullable=False)
    
    # Relationship: Member → Group
    group = relationship("GroupORM", back_populates="members")
