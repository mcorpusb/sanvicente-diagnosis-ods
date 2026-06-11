"""Tests for ODS export service."""
import io
import pytest

from app.models.diagnosis import DiagnosisRecord, SHEETS_HEADER
from app.services.ods_service import generate_ods, ods_filename


def _make_record(vehicle_id="1234ABC", make="Toyota", model="Corolla",
                 year=2019, mileage=80000, fault_codes=None,
                 symptoms="Ninguno", technician="Técnico Prueba",
                 ai_diagnosis="Diagnóstico de prueba",
                 ai_recommendations="Recomendaciones de prueba",
                 record_id="TEST001") -> DiagnosisRecord:
    return DiagnosisRecord(
        vehicle_id=vehicle_id,
        make=make,
        model=model,
        year=year,
        mileage=mileage,
        fault_codes=fault_codes or ["P0301"],
        symptoms=symptoms,
        technician=technician,
        ai_diagnosis=ai_diagnosis,
        ai_recommendations=ai_recommendations,
        record_id=record_id,
    )


class TestGenerateOds:
    def test_returns_bytes(self):
        records = [_make_record()]
        result = generate_ods(records)
        assert isinstance(result, bytes)

    def test_non_empty_output(self):
        records = [_make_record()]
        result = generate_ods(records)
        assert len(result) > 0

    def test_empty_records_list(self):
        result = generate_ods([])
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_ods_magic_bytes(self):
        """ODS files are ZIP archives; first bytes should be PK magic."""
        records = [_make_record()]
        result = generate_ods(records)
        assert result[:2] == b"PK", "ODS file should start with ZIP magic bytes"

    def test_multiple_records(self):
        records = [
            _make_record(vehicle_id="0001AAA", record_id="REC001"),
            _make_record(vehicle_id="0002BBB", record_id="REC002"),
            _make_record(vehicle_id="0003CCC", record_id="REC003"),
        ]
        result = generate_ods(records)
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_unicode_content_does_not_raise(self):
        record = _make_record(
            make="Citroën",
            model="Berlingo",
            symptoms="Tirones, pérdida de potencia ñ áéíóú",
            ai_diagnosis="Avería en el sistema de inyección.",
        )
        result = generate_ods([record])
        assert isinstance(result, bytes)


class TestOdsFilename:
    def test_has_ods_extension(self):
        name = ods_filename()
        assert name.endswith(".ods")

    def test_has_prefix(self):
        name = ods_filename("export")
        assert name.startswith("export_")

    def test_custom_prefix(self):
        name = ods_filename("diagnosticos")
        assert name.startswith("diagnosticos_")
