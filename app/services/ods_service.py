"""ODS (OpenDocument Spreadsheet) export service."""
import io
import logging
from datetime import datetime

from odf.opendocument import OpenDocumentSpreadsheet  # type: ignore
from odf.style import (  # type: ignore
    Style,
    TextProperties,
    TableColumnProperties,
)
from odf.table import Table, TableColumn, TableRow, TableCell  # type: ignore
from odf.text import P  # type: ignore

from app.models.diagnosis import DiagnosisRecord, SHEETS_HEADER

logger = logging.getLogger(__name__)


def _make_header_style(doc: OpenDocumentSpreadsheet) -> Style:
    style = Style(name="HeaderCell", family="table-cell")
    style.addElement(TextProperties(fontweight="bold", color="#FFFFFF"))
    doc.styles.addElement(style)
    return style


def _make_col_style(doc: OpenDocumentSpreadsheet, width: str) -> Style:
    style = Style(name=f"Col{width}", family="table-column")
    style.addElement(TableColumnProperties(columnwidth=width))
    doc.automaticstyles.addElement(style)
    return style


def _text_cell(value: str, style_name: str = "") -> TableCell:
    cell = TableCell(valuetype="string", stylename=style_name)
    cell.addElement(P(text=str(value)))
    return cell


def generate_ods(records: list[DiagnosisRecord]) -> bytes:
    """
    Generate an ODS file from a list of DiagnosisRecord objects.

    Returns the raw bytes of the ODS file.
    """
    doc = OpenDocumentSpreadsheet()

    header_style = _make_header_style(doc)

    table = Table(name="Diagnósticos")

    col_widths = ["2cm", "4cm", "2.5cm", "3cm", "3cm", "1.5cm",
                  "2.5cm", "5cm", "7cm", "3cm", "9cm", "9cm"]
    for width in col_widths:
        col_style = Style(name=f"ColWidth{width.replace('.', '_')}", family="table-column")
        col_style.addElement(TableColumnProperties(columnwidth=width))
        doc.automaticstyles.addElement(col_style)
        table.addElement(TableColumn(stylename=col_style.getAttribute("name")))

    header_row = TableRow()
    for header_text in SHEETS_HEADER:
        header_row.addElement(_text_cell(header_text, style_name=header_style.getAttribute("name")))
    table.addElement(header_row)

    for record in records:
        row = TableRow()
        for value in record.to_sheets_row():
            row.addElement(_text_cell(value))
        table.addElement(row)

    doc.spreadsheet.addElement(table)

    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()


def ods_filename(prefix: str = "diagnosticos") -> str:
    """Generate a timestamped ODS filename."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{ts}.ods"
