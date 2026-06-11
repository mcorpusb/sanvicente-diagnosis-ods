"""ODS export route."""
import logging

from flask import Blueprint, Response

from app.services.sheets_service import fetch_all_records
from app.services.ods_service import generate_ods, ods_filename

logger = logging.getLogger(__name__)

bp = Blueprint("export", __name__)


@bp.route("/api/export/ods")
def export_ods():
    """Generate and download an ODS file with all diagnosis records."""
    records = fetch_all_records()
    ods_bytes = generate_ods(records)
    filename = ods_filename()

    return Response(
        ods_bytes,
        mimetype="application/vnd.oasis.opendocument.spreadsheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
