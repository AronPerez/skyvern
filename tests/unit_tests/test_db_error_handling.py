from unittest.mock import patch

import pytest
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from skyvern.forge.sdk.db._error_handling import db_operation
from skyvern.forge.sdk.db.exceptions import NotFoundError


class TestDbOperationSuccess:
    """Happy-path behavior."""

    @pytest.mark.asyncio
    async def test_returns_value(self) -> None:
        @db_operation("test_op")
        async def happy() -> str:
            return "ok"

        assert await happy() == "ok"

    @pytest.mark.asyncio
    async def test_passes_args_and_kwargs(self) -> None:
        @db_operation("test_op")
        async def echo(a: int, b: str, *, flag: bool = False) -> tuple[int, str, bool]:
            return (a, b, flag)

        assert await echo(1, "x", flag=True) == (1, "x", True)

    @pytest.mark.asyncio
    async def test_works_as_method(self) -> None:
        class FakeDB:
            @db_operation("get_item")
            async def get_item(self, item_id: str) -> str:
                return f"item-{item_id}"

        db = FakeDB()
        assert await db.get_item("42") == "item-42"


class TestNotFoundErrorPassthrough:
    """NotFoundError must be re-raised without logging."""

    @pytest.mark.asyncio
    async def test_reraises_not_found_error(self) -> None:
        @db_operation("test_op")
        async def raises_not_found() -> None:
            raise NotFoundError("missing")

        with pytest.raises(NotFoundError, match="missing"):
            await raises_not_found()

    @pytest.mark.asyncio
    async def test_not_found_error_is_not_logged(self) -> None:
        @db_operation("test_op")
        async def raises_not_found() -> None:
            raise NotFoundError("missing")

        with patch("skyvern.forge.sdk.db._error_handling.LOG") as mock_log:
            with pytest.raises(NotFoundError):
                await raises_not_found()

            mock_log.exception.assert_not_called()
            mock_log.error.assert_not_called()


class TestSQLAlchemyErrorHandling:
    """SQLAlchemyError must be logged and re-raised."""

    @pytest.mark.asyncio
    async def test_reraises_sqlalchemy_error(self) -> None:
        @db_operation("test_op")
        async def raises_sqla() -> None:
            raise SQLAlchemyError("db boom")

        with pytest.raises(SQLAlchemyError):
            await raises_sqla()

    @pytest.mark.asyncio
    async def test_logs_sqlalchemy_error_with_operation(self) -> None:
        @db_operation("create_task")
        async def raises_sqla() -> None:
            raise SQLAlchemyError("db boom")

        with patch("skyvern.forge.sdk.db._error_handling.LOG") as mock_log:
            with pytest.raises(SQLAlchemyError):
                await raises_sqla()

            mock_log.exception.assert_called_once_with("SQLAlchemyError", operation="create_task")

    @pytest.mark.asyncio
    async def test_catches_sqlalchemy_subclass(self) -> None:
        @db_operation("test_op")
        async def raises_integrity() -> None:
            raise IntegrityError("INSERT ...", params={}, orig=Exception("duplicate key"))

        with patch("skyvern.forge.sdk.db._error_handling.LOG") as mock_log:
            with pytest.raises(IntegrityError):
                await raises_integrity()

            mock_log.exception.assert_called_once_with("SQLAlchemyError", operation="test_op")


class TestGenericExceptionHandling:
    """Generic Exception must be logged and re-raised."""

    @pytest.mark.asyncio
    async def test_reraises_generic_exception(self) -> None:
        @db_operation("test_op")
        async def raises_generic() -> None:
            raise RuntimeError("unexpected")

        with pytest.raises(RuntimeError, match="unexpected"):
            await raises_generic()

    @pytest.mark.asyncio
    async def test_logs_generic_exception_with_operation(self) -> None:
        @db_operation("update_workflow")
        async def raises_generic() -> None:
            raise RuntimeError("unexpected")

        with patch("skyvern.forge.sdk.db._error_handling.LOG") as mock_log:
            with pytest.raises(RuntimeError):
                await raises_generic()

            mock_log.exception.assert_called_once_with("UnexpectedError", operation="update_workflow")


class TestFunctools:
    """functools.wraps must preserve the original function's metadata."""

    def test_preserves_name(self) -> None:
        @db_operation("op")
        async def original_name() -> None:
            pass

        assert original_name.__name__ == "original_name"

    def test_preserves_qualname(self) -> None:
        @db_operation("op")
        async def original_name() -> None:
            pass

        assert "original_name" in original_name.__qualname__

    def test_preserves_docstring(self) -> None:
        @db_operation("op")
        async def documented() -> None:
            """Original docstring."""

        assert documented.__doc__ == "Original docstring."

    def test_preserves_module(self) -> None:
        @db_operation("op")
        async def modular() -> None:
            pass

        assert modular.__module__ == __name__

    def test_wrapped_attribute(self) -> None:
        async def original() -> None:
            pass

        decorated = db_operation("op")(original)
        assert decorated.__wrapped__ is original  # type: ignore[attr-defined]
