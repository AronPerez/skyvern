"""Tests for CLI utils - specifically sync_frontend_api_key functionality."""

import os
import shutil
from pathlib import Path

import pytest
from dotenv import load_dotenv, set_key


def sync_frontend_api_key_impl(
    backend_env_path: Path,
    frontend_env_path: Path | None,
) -> bool:
    """Test implementation of sync_frontend_api_key logic.

    This mirrors the logic in skyvern/cli/utils.py but without console output dependencies.
    """
    if frontend_env_path is None:
        return False

    frontend_dir = frontend_env_path.parent
    if not frontend_env_path.exists():
        example_env = frontend_dir / ".env.example"
        if example_env.exists():
            shutil.copy(example_env, frontend_env_path)
        else:
            return False

    if not backend_env_path.exists():
        return False

    load_dotenv(backend_env_path)
    skyvern_api_key = os.getenv("SKYVERN_API_KEY")
    if skyvern_api_key:
        set_key(frontend_env_path, "VITE_SKYVERN_API_KEY", skyvern_api_key)
        return True
    else:
        return False


class TestSyncFrontendApiKey:
    """Tests for the sync_frontend_api_key function logic."""

    @pytest.fixture(autouse=True)
    def clear_env(self):
        """Clear SKYVERN_API_KEY from environment before each test."""
        original = os.environ.pop("SKYVERN_API_KEY", None)
        yield
        if original is not None:
            os.environ["SKYVERN_API_KEY"] = original
        else:
            os.environ.pop("SKYVERN_API_KEY", None)

    @pytest.fixture
    def setup_env_files(self, tmp_path: Path):
        """Set up temporary backend and frontend env files."""
        backend_env = tmp_path / ".env"
        backend_env.write_text("SKYVERN_API_KEY=test-api-key-12345\n")

        frontend_dir = tmp_path / "skyvern-frontend"
        frontend_dir.mkdir()
        frontend_example = frontend_dir / ".env.example"
        frontend_example.write_text("VITE_API_BASE_URL=http://localhost:8000\nVITE_SKYVERN_API_KEY=\n")

        return tmp_path, frontend_dir

    def test_sync_api_key_creates_frontend_env_from_example(self, setup_env_files):
        """Frontend .env should be created from .env.example if it doesn't exist."""
        tmp_path, frontend_dir = setup_env_files
        backend_env = tmp_path / ".env"
        frontend_env = frontend_dir / ".env"

        result = sync_frontend_api_key_impl(backend_env, frontend_env)

        assert result is True
        assert frontend_env.exists()
        content = frontend_env.read_text()
        assert "VITE_SKYVERN_API_KEY" in content
        assert "test-api-key-12345" in content

    def test_sync_api_key_updates_existing_frontend_env(self, setup_env_files):
        """Existing frontend .env should be updated with the API key."""
        tmp_path, frontend_dir = setup_env_files
        backend_env = tmp_path / ".env"
        frontend_env = frontend_dir / ".env"
        frontend_env.write_text("VITE_API_BASE_URL=http://localhost:8000\nVITE_SKYVERN_API_KEY=old-key\n")

        result = sync_frontend_api_key_impl(backend_env, frontend_env)

        assert result is True
        content = frontend_env.read_text()
        assert "test-api-key-12345" in content
        assert "old-key" not in content

    def test_sync_api_key_returns_false_when_frontend_not_found(self, tmp_path: Path):
        """Should return False when frontend directory is not found."""
        backend_env = tmp_path / ".env"
        backend_env.write_text("SKYVERN_API_KEY=test-key\n")

        result = sync_frontend_api_key_impl(backend_env, None)

        assert result is False

    def test_sync_api_key_returns_false_when_backend_env_missing(self, tmp_path: Path):
        """Should return False when backend .env doesn't exist."""
        frontend_dir = tmp_path / "skyvern-frontend"
        frontend_dir.mkdir()
        frontend_env = frontend_dir / ".env"
        frontend_env.write_text("VITE_SKYVERN_API_KEY=\n")

        result = sync_frontend_api_key_impl(tmp_path / ".env", frontend_env)

        assert result is False

    def test_sync_api_key_returns_false_when_api_key_not_set(self, tmp_path: Path):
        """Should return False when SKYVERN_API_KEY is not in backend .env."""
        backend_env = tmp_path / ".env"
        backend_env.write_text("OTHER_VAR=value\n")

        frontend_dir = tmp_path / "skyvern-frontend"
        frontend_dir.mkdir()
        frontend_env = frontend_dir / ".env"
        frontend_env.write_text("VITE_SKYVERN_API_KEY=\n")

        result = sync_frontend_api_key_impl(backend_env, frontend_env)

        assert result is False

    def test_sync_api_key_returns_false_when_no_example_env(self, tmp_path: Path):
        """Should return False when frontend .env and .env.example don't exist."""
        backend_env = tmp_path / ".env"
        backend_env.write_text("SKYVERN_API_KEY=test-key\n")

        frontend_dir = tmp_path / "skyvern-frontend"
        frontend_dir.mkdir()
        frontend_env = frontend_dir / ".env"

        result = sync_frontend_api_key_impl(backend_env, frontend_env)

        assert result is False
        assert not frontend_env.exists()

    def test_sync_api_key_preserves_other_frontend_vars(self, setup_env_files):
        """Other frontend env vars should be preserved when syncing API key."""
        tmp_path, frontend_dir = setup_env_files
        backend_env = tmp_path / ".env"
        frontend_env = frontend_dir / ".env"
        frontend_env.write_text(
            "VITE_API_BASE_URL=http://localhost:9000\nVITE_SKYVERN_API_KEY=old-key\nVITE_CUSTOM_VAR=custom-value\n"
        )

        result = sync_frontend_api_key_impl(backend_env, frontend_env)

        assert result is True
        content = frontend_env.read_text()
        assert "VITE_API_BASE_URL" in content
        assert "http://localhost:9000" in content
        assert "VITE_CUSTOM_VAR" in content
        assert "custom-value" in content
        assert "test-api-key-12345" in content
