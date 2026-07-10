from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from google.auth.exceptions import RefreshError


def _make_creds(*, valid: bool, expired: bool, refresh_token: str | None = "tok") -> MagicMock:
    creds = MagicMock()
    creds.valid = valid
    creds.expired = expired
    creds.refresh_token = refresh_token
    creds.to_json.return_value = "{}"
    return creds


class TestGetCredentials:
    def test_refresh_success(self, tmp_path, monkeypatch):
        """Expired-but-refreshable token refreshes silently without launching a browser."""
        token_file = tmp_path / "token.json"
        token_file.write_text("{}")
        monkeypatch.setenv("CREATOR_SEO_TOKEN_PATH", str(token_file))

        creds = _make_creds(valid=False, expired=True)
        creds.refresh.side_effect = lambda _: setattr(creds, "valid", True)

        with (
            patch("creator_seo_mcp.gsc.Credentials.from_authorized_user_file", return_value=creds),
            patch("creator_seo_mcp.gsc.InstalledAppFlow") as mock_flow,
            patch("creator_seo_mcp.gsc._is_headless", return_value=False),
        ):
            from creator_seo_mcp.gsc import _get_credentials

            result = _get_credentials()

        assert result is creds
        mock_flow.from_client_secrets_file.assert_not_called()

    def test_refresh_error_interactive_launches_browser(self, tmp_path, monkeypatch):
        """RefreshError in an interactive terminal falls through to run_local_server."""
        token_file = tmp_path / "token.json"
        token_file.write_text("{}")
        monkeypatch.setenv("CREATOR_SEO_TOKEN_PATH", str(token_file))
        monkeypatch.delenv("CREATOR_SEO_HEADLESS", raising=False)

        creds = _make_creds(valid=False, expired=True)
        creds.refresh.side_effect = RefreshError("invalid_grant")

        new_creds = _make_creds(valid=True, expired=False)
        mock_flow_instance = MagicMock()
        mock_flow_instance.run_local_server.return_value = new_creds

        with (
            patch("creator_seo_mcp.gsc.Credentials.from_authorized_user_file", return_value=creds),
            patch("creator_seo_mcp.gsc.InstalledAppFlow.from_client_secrets_file", return_value=mock_flow_instance),
            patch("creator_seo_mcp.gsc._is_headless", return_value=False),
            patch("creator_seo_mcp.gsc.credentials_path", return_value="/fake/credentials.json"),
        ):
            from creator_seo_mcp.gsc import _get_credentials

            result = _get_credentials()

        mock_flow_instance.run_local_server.assert_called_once_with(port=0)
        assert result is new_creds

    def test_refresh_error_headless_raises(self, tmp_path, monkeypatch):
        """RefreshError in a headless/scheduled context raises RuntimeError instead of hanging."""
        token_file = tmp_path / "token.json"
        token_file.write_text("{}")
        monkeypatch.setenv("CREATOR_SEO_TOKEN_PATH", str(token_file))
        monkeypatch.setenv("CREATOR_SEO_HEADLESS", "1")

        creds = _make_creds(valid=False, expired=True)
        creds.refresh.side_effect = RefreshError("invalid_grant")

        with (
            patch("creator_seo_mcp.gsc.Credentials.from_authorized_user_file", return_value=creds),
            patch("creator_seo_mcp.gsc.InstalledAppFlow") as mock_flow,
        ):
            from creator_seo_mcp.gsc import _get_credentials

            with pytest.raises(RuntimeError, match="Re-authenticate"):
                _get_credentials()

        mock_flow.from_client_secrets_file.assert_not_called()
