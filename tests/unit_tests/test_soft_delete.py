from __future__ import annotations

import datetime
from unittest.mock import patch

from sqlalchemy import Column, DateTime, String, select
from sqlalchemy.orm import DeclarativeBase

from skyvern.forge.sdk.db._soft_delete import SoftDeleteMixin


# Minimal in-memory model for testing (no real DB needed)
class FakeBase(DeclarativeBase):
    pass


class FakeModel(SoftDeleteMixin, FakeBase):
    __tablename__ = "fake"
    id = Column(String, primary_key=True)
    deleted_at = Column(DateTime, nullable=True)


class TestSoftDeleteMixin:
    def test_exclude_deleted_adds_filter(self) -> None:
        query = select(FakeModel)
        filtered = FakeModel.exclude_deleted(query)
        compiled = str(filtered.compile(compile_kwargs={"literal_binds": True}))
        assert "deleted_at IS NULL" in compiled

    def test_exclude_deleted_preserves_existing_filters(self) -> None:
        query = select(FakeModel).where(FakeModel.id == "abc")
        filtered = FakeModel.exclude_deleted(query)
        compiled = str(filtered.compile(compile_kwargs={"literal_binds": True}))
        assert "deleted_at IS NULL" in compiled
        assert "fake.id" in compiled

    def test_exclude_deleted_returns_new_query(self) -> None:
        query = select(FakeModel)
        filtered = FakeModel.exclude_deleted(query)
        assert filtered is not query

    def test_mark_deleted_sets_deleted_at(self) -> None:
        instance = FakeModel(id="test-1")
        assert instance.deleted_at is None
        instance.mark_deleted()
        assert instance.deleted_at is not None
        assert isinstance(instance.deleted_at, datetime.datetime)

    def test_mark_deleted_uses_utcnow(self) -> None:
        fake_now = datetime.datetime(2026, 1, 1, 12, 0, 0)
        instance = FakeModel(id="test-2")
        with patch("skyvern.forge.sdk.db._soft_delete.datetime") as mock_dt:
            mock_dt.datetime.utcnow.return_value = fake_now
            instance.mark_deleted()
        assert instance.deleted_at == fake_now

    def test_mark_deleted_updates_on_subsequent_calls(self) -> None:
        instance = FakeModel(id="test-3")
        instance.mark_deleted()
        first = instance.deleted_at
        instance.mark_deleted()
        second = instance.deleted_at
        assert second is not None
        assert second >= first

    def test_soft_delete_values_returns_dict(self) -> None:
        values = FakeModel.soft_delete_values()
        assert "deleted_at" in values
        assert isinstance(values["deleted_at"], datetime.datetime)

    def test_soft_delete_values_uses_utcnow(self) -> None:
        fake_now = datetime.datetime(2026, 1, 1, 12, 0, 0)
        with patch("skyvern.forge.sdk.db._soft_delete.datetime") as mock_dt:
            mock_dt.datetime.utcnow.return_value = fake_now
            values = FakeModel.soft_delete_values()
        assert values["deleted_at"] == fake_now

    def test_deleted_at_column_is_nullable(self) -> None:
        col = FakeModel.__table__.columns["deleted_at"]
        assert col.nullable is True
        assert isinstance(col.type, DateTime)
