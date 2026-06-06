import os
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, JSON, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
from typing import List, Dict, Any, Optional

from config.settings import settings
from config.logger import setup_logger

logger = setup_logger("memory.postgres_store")

Base = declarative_base()

class Tenant(Base):
    __tablename__ = 'tenants'
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = 'users'
    id = Column(String, primary_key=True)
    tenant_id = Column(String, ForeignKey('tenants.id'), nullable=False)
    phone_number = Column(String, unique=True, nullable=True)
    role = Column(String, default="user") # e.g., admin, user, guest
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    tenant = relationship("Tenant")

class Session(Base):
    __tablename__ = 'sessions'
    session_id = Column(String, primary_key=True)
    tenant_id = Column(String, ForeignKey('tenants.id'), nullable=False)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata_col = Column(JSON, default={})

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String, ForeignKey('tenants.id'), nullable=False)
    session_id = Column(String, ForeignKey('sessions.session_id'), nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    tokens = Column(Integer, default=0)

class MessageFeedback(Base):
    __tablename__ = 'message_feedback'
    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(Integer, ForeignKey('messages.id'), nullable=False)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    tenant_id = Column(String, ForeignKey('tenants.id'), nullable=False)
    rating = Column(Integer, nullable=False) # 1 for positive, -1 for negative
    timestamp = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = 'audit_log'
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String, ForeignKey('tenants.id'), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    action = Column(String, nullable=False)
    user_id = Column(String, nullable=True)
    details = Column(JSON, default={})


class PostgresStore:
    def __init__(self):
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            logger.warning("DATABASE_URL not set, falling back to SQLite in-memory for testing")
            db_url = "sqlite:///:memory:"
            
        # Convert postgres:// to postgresql:// for SQLAlchemy
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)

        self.engine = create_engine(db_url)
        # We assume the database is fresh or migrated properly
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        logger.info("PostgreSQL database initialized with Multi-Tenancy.")

    def get_user_by_phone(self, phone_number: str) -> Optional[User]:
        with self.SessionLocal() as db:
            return db.query(User).filter(User.phone_number == phone_number, User.is_active == True).first()

    def create_session(self, session_id: str, tenant_id: str, user_id: str, metadata: Dict[str, Any] = None) -> None:
        with self.SessionLocal() as db:
            session = db.query(Session).filter(Session.session_id == session_id, Session.tenant_id == tenant_id).first()
            if not session:
                new_session = Session(session_id=session_id, tenant_id=tenant_id, user_id=user_id, metadata_col=metadata or {})
                db.add(new_session)
                db.commit()

    def add_message(self, session_id: str, tenant_id: str, role: str, content: str, tokens: int = 0) -> None:
        with self.SessionLocal() as db:
            msg = Message(session_id=session_id, tenant_id=tenant_id, role=role, content=content, tokens=tokens)
            db.add(msg)
            
            session = db.query(Session).filter(Session.session_id == session_id, Session.tenant_id == tenant_id).first()
            if session:
                session.updated_at = datetime.utcnow()
            db.commit()

    def get_recent_messages(self, session_id: str, tenant_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        with self.SessionLocal() as db:
            messages = db.query(Message).filter(Message.session_id == session_id, Message.tenant_id == tenant_id).order_by(Message.timestamp.desc()).limit(limit).all()
            return [{"role": m.role, "content": m.content, "timestamp": m.timestamp} for m in reversed(messages)]

    def log_audit_event(self, action: str, tenant_id: Optional[str] = None, user_id: Optional[str] = None, details: Dict[str, Any] = None) -> None:
        with self.SessionLocal() as db:
            log = AuditLog(action=action, tenant_id=tenant_id, user_id=user_id, details=details or {})
            db.add(log)
            db.commit()

    def add_message_feedback(self, message_id: int, user_id: str, tenant_id: str, rating: int) -> None:
        with self.SessionLocal() as db:
            feedback = MessageFeedback(message_id=message_id, user_id=user_id, tenant_id=tenant_id, rating=rating)
            db.add(feedback)
            db.commit()
