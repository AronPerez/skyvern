"""Tests for manual 2FA input without pre-configured TOTP credentials (SKY-6)."""

import pytest

from skyvern.forge.sdk.db.agent_db import AgentDB


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
