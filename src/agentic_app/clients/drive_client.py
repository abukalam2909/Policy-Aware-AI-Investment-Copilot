"""Google Drive upload client — uses service account credentials."""

import json
import os
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload

_SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def _load_config() -> dict:
    config_path = Path(__file__).resolve().parents[3] / "delivery_config.json"
    if config_path.exists():
        return json.loads(config_path.read_text(encoding="utf-8"))
    return {}


def _get_delivery_settings() -> tuple[str, str]:
    """Return (service_account_path, drive_folder_id)."""
    config = _load_config()

    sa_path_raw = (
        os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
        or config.get("GOOGLE_SERVICE_ACCOUNT_FILE", "")
    )
    if not sa_path_raw:
        raise RuntimeError(
            "Google service account file not configured. Add "
            "GOOGLE_SERVICE_ACCOUNT_FILE to delivery_config.json."
        )
    project_root = Path(__file__).resolve().parents[3]
    resolved = (project_root / sa_path_raw).resolve()
    if not resolved.exists():
        raise RuntimeError(f"Service account file not found: {resolved}")

    folder_id = (
        os.getenv("GOOGLE_DRIVE_FOLDER_ID")
        or config.get("GOOGLE_DRIVE_FOLDER_ID", "")
    )
    if not folder_id:
        raise RuntimeError(
            "Google Drive folder ID not configured. Add "
            "GOOGLE_DRIVE_FOLDER_ID to delivery_config.json."
        )

    return str(resolved), folder_id


def upload_report(filename: str, content: str) -> str:
    """Upload an HTML report into the shared Drive folder and return a public link."""
    sa_path, folder_id = _get_delivery_settings()

    credentials = service_account.Credentials.from_service_account_file(
        sa_path, scopes=_SCOPES
    )
    service = build("drive", "v3", credentials=credentials, cache_discovery=False)

    file_metadata = {
        "name": filename,
        "mimeType": "text/html",
        "parents": [folder_id],
    }
    media = MediaInMemoryUpload(
        content.encode("utf-8"), mimetype="text/html", resumable=False
    )

    uploaded = (
        service.files()
        .create(body=file_metadata, media_body=media, fields="id,webViewLink")
        .execute()
    )

    file_id = uploaded["id"]

    service.permissions().create(
        fileId=file_id,
        body={"type": "anyone", "role": "reader"},
    ).execute()

    return uploaded.get("webViewLink", f"https://drive.google.com/file/d/{file_id}/view")
