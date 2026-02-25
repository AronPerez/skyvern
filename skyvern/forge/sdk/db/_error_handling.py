from __future__ import annotations

import functools
from typing import Any, Callable, TypeVar

import structlog
from sqlalchemy.exc import SQLAlchemyError

from skyvern.forge.sdk.db.exceptions import NotFoundError

LOG = structlog.get_logger()

F = TypeVar("F", bound=Callable[..., Any])


def db_operation(operation_name: str) -> Callable[[F], F]:
    """Decorator that wraps async database methods in standardized error handling.

    Catches and handles exceptions uniformly:
    - NotFoundError: re-raised as-is (no logging)
    - SQLAlchemyError: logged via LOG.exception() with operation context, then re-raised
    - Exception: logged via LOG.exception() with operation context, then re-raised

    Args:
        operation_name: Human-readable name for log context (e.g., "get_task").

    Example::

        @db_operation("get_task")
        async def get_task(self, task_id: str) -> Task:
            async with self.Session() as session:
                # just the happy path
    """

    def decorator(fn: F) -> F:
        @functools.wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return await fn(*args, **kwargs)
            except NotFoundError:
                raise
            except SQLAlchemyError:
                LOG.exception("SQLAlchemyError", operation=operation_name)
                raise
            except Exception:
                LOG.exception("UnexpectedError", operation=operation_name)
                raise

        return wrapper  # type: ignore[return-value]

    return decorator
