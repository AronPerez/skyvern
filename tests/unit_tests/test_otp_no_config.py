"""Tests for manual 2FA input without pre-configured TOTP credentials (SKY-6)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from skyvern.forge.agent import ForgeAgent
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


# === Task 6: Integration test — handle_potential_OTP_actions without TOTP config ===


@pytest.mark.asyncio
async def test_handle_potential_OTP_actions_without_totp_config():
    """When LLM detects 2FA but no TOTP config exists, should still enter verification flow."""
    agent = ForgeAgent.__new__(ForgeAgent)

    task = MagicMock()
    task.organization_id = "org_1"
    task.totp_verification_url = None
    task.totp_identifier = None
    task.task_id = "tsk_1"
    task.workflow_run_id = None

    step = MagicMock()
    scraped_page = MagicMock()
    browser_state = MagicMock()

    json_response = {
        "should_enter_verification_code": True,
        "place_to_enter_verification_code": "input#otp-code",
        "actions": [],
    }

    with patch.object(agent, "handle_potential_verification_code", new_callable=AsyncMock) as mock_handler:
        mock_handler.return_value = {"actions": []}
        with patch("skyvern.forge.agent.parse_actions", return_value=[]):
            result_json, result_actions = await agent.handle_potential_OTP_actions(
                task, step, scraped_page, browser_state, json_response
            )
        mock_handler.assert_called_once()


@pytest.mark.asyncio
async def test_handle_potential_OTP_actions_skips_magic_link_without_totp_config():
    """Magic links should still require TOTP config."""
    agent = ForgeAgent.__new__(ForgeAgent)

    task = MagicMock()
    task.organization_id = "org_1"
    task.totp_verification_url = None
    task.totp_identifier = None

    step = MagicMock()
    scraped_page = MagicMock()
    browser_state = MagicMock()

    json_response = {
        "should_verify_by_magic_link": True,
    }

    with patch.object(agent, "handle_potential_magic_link", new_callable=AsyncMock) as mock_handler:
        result_json, result_actions = await agent.handle_potential_OTP_actions(
            task, step, scraped_page, browser_state, json_response
        )
        mock_handler.assert_not_called()
    assert result_actions == []
