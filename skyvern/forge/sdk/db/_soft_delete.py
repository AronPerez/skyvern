from __future__ import annotations

import datetime
from typing import Any

from sqlalchemy import Column


class SoftDeleteMixin:
    """Mixin for SQLAlchemy models with soft-delete support.

    Provides a ``deleted_at`` column and helper methods for soft-delete
    operations.

    Usage::

        class WorkflowModel(SoftDeleteMixin, Base):
            ...

        # In queries:
        query = WorkflowModel.exclude_deleted(select(WorkflowModel))

        # For deletion:
        workflow.mark_deleted()

        # For bulk deletion:
        stmt = update(WorkflowModel).values(**WorkflowModel.soft_delete_values())
    """

    deleted_at: Column  # type: ignore[type-arg]

    @classmethod
    def exclude_deleted(cls, query: Any) -> Any:
        """Filter a query to exclude soft-deleted rows."""
        return query.filter(cls.deleted_at.is_(None))

    def mark_deleted(self) -> None:
        """Mark this instance as soft-deleted by setting ``deleted_at`` to now."""
        self.deleted_at = datetime.datetime.utcnow()  # type: ignore[assignment]

    @classmethod
    def soft_delete_values(cls) -> dict[str, datetime.datetime]:
        """Return values dict for bulk soft-delete update statements."""
        return {"deleted_at": datetime.datetime.utcnow()}
