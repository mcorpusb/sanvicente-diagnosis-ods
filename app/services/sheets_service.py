"""Google Sheets integration service."""
import os
import logging
import uuid
from typing import Optional

from app.models.diagnosis import DiagnosisRecord, SHEETS_HEADER

logger = logging.getLogger(__name__)


def _get_service():
    """Build and return an authenticated Google Sheets API service."""
    from google.oauth2 import service_account  # type: ignore
    from googleapiclient.discovery import build  # type: ignore

    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials_file = os.environ.get("GOOGLE_SERVICE_ACCOUNT_FILE", "service_account.json")
    credentials = service_account.Credentials.from_service_account_file(
        credentials_file, scopes=scopes
    )
    return build("sheets", "v4", credentials=credentials)


def _spreadsheet_id() -> str:
    return os.environ.get("SPREADSHEET_ID", "")


def _sheet_name() -> str:
    return os.environ.get("SHEET_NAME", "Diagnosticos")


def ensure_header() -> None:
    """Create the header row if the sheet is empty."""
    spreadsheet_id = _spreadsheet_id()
    if not spreadsheet_id:
        return
    try:
        service = _get_service()
        sheet = service.spreadsheets()
        range_name = f"{_sheet_name()}!A1:L1"
        result = sheet.values().get(
            spreadsheetId=spreadsheet_id, range=range_name
        ).execute()
        existing = result.get("values", [])
        if not existing:
            sheet.values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption="RAW",
                body={"values": [SHEETS_HEADER]},
            ).execute()
            logger.info("Cabecera creada en Google Sheets.")
    except Exception as exc:  # noqa: BLE001
        logger.error("Error al inicializar cabecera en Sheets: %s", exc)


def append_record(record: DiagnosisRecord) -> Optional[str]:
    """Append a diagnosis record to the Google Sheet. Returns the generated record_id."""
    spreadsheet_id = _spreadsheet_id()
    if not spreadsheet_id:
        logger.warning("SPREADSHEET_ID no configurado; omitiendo escritura en Sheets.")
        return None

    if not record.record_id:
        record.record_id = str(uuid.uuid4())[:8].upper()

    try:
        service = _get_service()
        range_name = f"{_sheet_name()}!A:L"
        service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={"values": [record.to_sheets_row()]},
        ).execute()
        logger.info("Registro %s añadido a Google Sheets.", record.record_id)
        return record.record_id
    except Exception as exc:  # noqa: BLE001
        logger.error("Error al escribir en Google Sheets: %s", exc)
        return None


def fetch_all_records() -> list[DiagnosisRecord]:
    """Fetch all diagnosis records from the Google Sheet (skipping header)."""
    spreadsheet_id = _spreadsheet_id()
    if not spreadsheet_id:
        logger.warning("SPREADSHEET_ID no configurado; devolviendo lista vacía.")
        return []

    try:
        service = _get_service()
        range_name = f"{_sheet_name()}!A2:L"
        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=range_name)
            .execute()
        )
        rows = result.get("values", [])
        return [DiagnosisRecord.from_sheets_row(row) for row in rows]
    except Exception as exc:  # noqa: BLE001
        logger.error("Error al leer de Google Sheets: %s", exc)
        return []
