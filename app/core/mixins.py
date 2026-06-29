from typing import Any

from sqlalchemy import Column, Integer, String, DateTime, event
from datetime import datetime, timezone


class TimestampMixin:
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class SoftDeleteMixin:
    is_deleted = Column(Integer, default=0)
    deleted_at = Column(DateTime, nullable=True)


def set_created_at(target, mapper):
    if target.created_at is None:
        target.created_at = datetime.now(timezone.utc)


def set_updated_at(target, mapper):
    target.updated_at = datetime.now(timezone.utc)


event.listen(TimestampMixin, "before_insert", set_created_at)
event.listen(TimestampMixin, "before_update", set_updated_at)
