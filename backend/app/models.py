from sqlalchemy import Boolean, Column, ForeignKey
from sqlalchemy import Integer, String, DateTime, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

# Association table for many-to-many relationship between activities and tags
activity_tags = Table(
    "activity_tags",
    Base.metadata,
    Column("activity_id", Integer, ForeignKey("activities.id")),
    Column("tag_id", Integer, ForeignKey("tags.id")),
)

# User database model


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    telegram_chat_id = Column(String, nullable=True)
    activities = relationship("Activity", back_populates="user")


# Activity database model


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration = Column(Integer, nullable=True)  # Duration in seconds

    # Timer related fields
    # Total recorded time in seconds
    recorded_time = Column(Integer, default=0)
    # stopped, running, paused
    timer_status = Column(String, default="stopped")
    last_timer_start = Column(
        DateTime(timezone=True), nullable=True
    )  # When timer was last started
    scheduled_time = Column(DateTime(timezone=True), nullable=True)  # When the task is scheduled for

    notified = Column(Boolean, default=False)  # Whether notification was sent

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="activities")
    tags = relationship("Tag", secondary=activity_tags, back_populates="activities")


# Tag database model


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    activities = relationship(
        "Activity", secondary=activity_tags, back_populates="tags"
    )
