from __future__ import annotations

import os
from datetime import date, timedelta
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .config import credentials_path, token_path

SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]


def _get_credentials() -> Credentials:
    token = token_path()
    creds: Credentials | None = None

    if os.path.exists(token):
        creds = Credentials.from_authorized_user_file(token, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path(), SCOPES)
            creds = flow.run_local_server(port=0)

        os.makedirs(os.path.dirname(token), exist_ok=True)
        with open(token, "w") as f:
            f.write(creds.to_json())

    return creds


def get_service() -> Any:
    return build("searchconsole", "v1", credentials=_get_credentials())


def list_verified_sites() -> list[str]:
    service = get_service()
    result = service.sites().list().execute()
    entries = result.get("siteEntry", [])
    return [e["siteUrl"] for e in entries if e.get("permissionLevel") != "siteUnverifiedUser"]


def _date_range(days: int) -> tuple[str, str]:
    end = date.today() - timedelta(days=3)
    start = end - timedelta(days=days - 1)
    return start.isoformat(), end.isoformat()


def query_search_analytics(
    service: Any,
    site_url: str,
    start_date: str,
    end_date: str,
    dimensions: list[str],
    row_limit: int = 25000,
    start_row: int = 0,
    filters: list[dict[str, str]] | None = None,
) -> list[dict[str, Any]]:
    body: dict[str, Any] = {
        "startDate": start_date,
        "endDate": end_date,
        "dimensions": dimensions,
        "rowLimit": row_limit,
        "startRow": start_row,
    }
    if filters:
        body["dimensionFilterGroups"] = [{"filters": filters}]

    try:
        response = service.searchanalytics().query(siteUrl=site_url, body=body).execute()
    except HttpError as e:
        raise RuntimeError(f"GSC API error: {e}") from e

    return response.get("rows", [])


def paginate_search_analytics(
    service: Any,
    site_url: str,
    start_date: str,
    end_date: str,
    dimensions: list[str],
    filters: list[dict[str, str]] | None = None,
    page_size: int = 25000,
) -> list[dict[str, Any]]:
    all_rows: list[dict[str, Any]] = []
    start_row = 0
    while True:
        rows = query_search_analytics(
            service,
            site_url,
            start_date,
            end_date,
            dimensions,
            row_limit=page_size,
            start_row=start_row,
            filters=filters,
        )
        all_rows.extend(rows)
        if len(rows) < page_size:
            break
        start_row += page_size
    return all_rows


def date_range_for(days: int) -> tuple[str, str]:
    return _date_range(days)
