"""Tests for manual 2FA input without pre-configured TOTP credentials (SKY-6)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from skyvern.forge.sdk.db.agent_db import AgentDB
from skyvern.services.otp_service import _get_otp_value_by_run, poll_otp_value


@pytest.mark.asyncio
async def test_get_otp_codes_by_run_exists():
    """get_otp_codes_by_run should exist on AgentDB."""
    assert hasattr(AgentDB, "get_otp_codes_by_run"), "AgentDB missing get_otp_codes_by_run method"


@pytest.mark.asyncio
async def test_get_otp_codes_by_run_returns_empty_without_identifiers():
    """get_otp_codes_by_run should return [] when neither task_id nor workflow_run_id is given."""
    db = AgentDB.__new__(AgentDB)
    result = await db.get_otp_codes_by_run(
        organization_id="org_1",
    )
    assert result == []


# === Task 2: _get_otp_value_by_run OTP service function ===


@pytest.mark.asyncio
async def test_get_otp_value_by_run_returns_code():
    """_get_otp_value_by_run should find OTP codes by task_id."""
    mock_code = MagicMock()
    mock_code.code = "123456"
    mock_code.otp_type = "totp"

    mock_db = AsyncMock()
    mock_db.get_otp_codes_by_run.return_value = [mock_code]

    mock_app = MagicMock()
    mock_app.DATABASE = mock_db

    with patch("skyvern.services.otp_service.app", new=mock_app):
        result = await _get_otp_value_by_run(
            organization_id="org_1",
            task_id="tsk_1",
        )
    assert result is not None
    assert result.value == "123456"


@pytest.mark.asyncio
async def test_get_otp_value_by_run_returns_none_when_no_codes():
    """_get_otp_value_by_run should return None when no codes found."""
    mock_db = AsyncMock()
    mock_db.get_otp_codes_by_run.return_value = []

    mock_app = MagicMock()
    mock_app.DATABASE = mock_db

    with patch("skyvern.services.otp_service.app", new=mock_app):
        result = await _get_otp_value_by_run(
            organization_id="org_1",
            task_id="tsk_1",
        )
    assert result is None


# === Task 3: poll_otp_value without identifier ===


@pytest.mark.asyncio
async def test_poll_otp_value_without_identifier_uses_run_lookup():
    """poll_otp_value should use _get_otp_value_by_run when no identifier/URL provided."""
    mock_code = MagicMock()
    mock_code.code = "123456"
    mock_code.otp_type = "totp"

    mock_db = AsyncMock()
    mock_db.get_valid_org_auth_token.return_value = MagicMock(token="tok")
    mock_db.get_otp_codes_by_run.return_value = [mock_code]
    mock_db.update_task_2fa_state = AsyncMock()

    mock_app = MagicMock()
    mock_app.DATABASE = mock_db

    with (
        patch("skyvern.services.otp_service.app", new=mock_app),
        patch("skyvern.services.otp_service.asyncio.sleep", new_callable=AsyncMock),
    ):
        result = await poll_otp_value(
            organization_id="org_1",
            task_id="tsk_1",
        )
    assert result is not None
    assert result.value == "123456"
