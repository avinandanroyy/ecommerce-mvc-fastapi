from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Event, event
from sqlalchemy.orm import Session


def set_created_at(cls, target, event):
    if target.created_at is None:
        target.created_at = datetime.now(timezone.utc)


def set_updated_at(cls, target, event):
    if target.updated_at is None or event == "before_update":
        target.updated_at = datetime.now(timezone.utc)


def register_timestamps(Base):
    @event.listens_for(Base, "before_insert")
    def before_insert(mapper, connection, target):
        target.created_at = datetime.now(timezone.utc)
        target.updated_at = datetime.now(timezone.utc)

    @event.listens_for(Base, "before_update")
    def before_update(mapper, connection, target):
        target.updated_at = datetime.now(timezone.utc)
