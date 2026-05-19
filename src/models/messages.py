from datetime import datetime
import uuid

from sqlalchemy import Column, String, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.utils.db.base import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    role = Column(String, nullable=False)
    # Example:
    # "user"
    # "assistant"
    # "system"

    message = Column(Text, nullable=False)

    chat_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chat.id", ondelete="CASCADE"),
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationship
    chat = relationship("Chat", back_populates="messages")