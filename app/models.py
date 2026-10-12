from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey
from datetime import datetime, date

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(
        String(32),
        unique=True,
        nullable=False,
        index=True
    )

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = Column(
        String(255),
        nullable=False
    )

    tix = Column(
        Integer,
        default=0,
        nullable=False
    )

    webbux = Column(
        Integer, 
        default=0, 
        nullable=False
    )

    avatar = Column(
        String(50),
        default="default",
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

birth_date = Column(Date, nullable=True)

class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    token_hash = Column(
        String(64),
        unique=True,
        nullable=False,
        index=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    item_type = Column(String(50), nullable=False)
    description = Column(String(255), nullable=True)
    price = Column(Integer, default=0, nullable=False)
    currency = Column(String(20), default="tix", nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    template_path = Column(String(255), nullable=True)
    icon = Column(String(20), default="⭐", nullable=False)

class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    item_id = Column(
        Integer,
        ForeignKey("items.id"),
        nullable=False,
        index=True
    )

    equipped = Column(
        Integer,
        default=0,
        nullable=False
    )

class FriendRequest(Base):
    __tablename__ = "friend_requests"

    id = Column(Integer, primary_key=True, index=True)

    sender_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    receiver_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    status = Column(
        String(20),
        default="pending",
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
