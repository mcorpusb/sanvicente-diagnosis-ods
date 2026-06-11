"""Tests for DiagnosisRecord model."""
from datetime import datetime
import pytest

from app.models.diagnosis import DiagnosisRecord, SHEETS_HEADER


def _sample_record(**kwargs) -> DiagnosisRecord:
    defaults = dict(
        vehicle_id="1234ABC",
        make="Toyota",
        model="Corolla",
        year=2019,
        mileage=95000,
        fault_codes=["P0301", "P0420"],
        symptoms="Tirones en aceleración",
        technician="María García",
        ai_diagnosis="Fallo en cilindro 1 y catalizador deteriorado.",
        ai_recommendations="1. Verificar bujía del cilindro 1.\n2. Inspeccionar catalizador.",
        record_id="A1B2C3D4",
    )
    defaults.update(kwargs)
    return DiagnosisRecord(**defaults)


class TestDiagnosisRecordToSheetsRow:
    def test_row_length_matches_header(self):
        record = _sample_record()
        row = record.to_sheets_row()
        assert len(row) == len(SHEETS_HEADER)

    def test_row_values(self):
        record = _sample_record()
        row = record.to_sheets_row()
        assert row[0] == "A1B2C3D4"
        assert row[2] == "1234ABC"
        assert row[3] == "Toyota"
        assert row[4] == "Corolla"
        assert row[5] == "2019"
        assert row[6] == "95000"
        assert row[7] == "P0301, P0420"
        assert row[8] == "Tirones en aceleración"
        assert row[9] == "María García"

    def test_timestamp_format(self):
        fixed_ts = datetime(2024, 6, 15, 10, 30, 0)
        record = _sample_record(timestamp=fixed_ts)
        row = record.to_sheets_row()
        assert row[1] == "2024-06-15 10:30:00"

    def test_empty_record_id_becomes_empty_string(self):
        record = _sample_record(record_id=None)
        row = record.to_sheets_row()
        assert row[0] == ""

    def test_empty_fault_codes(self):
        record = _sample_record(fault_codes=[])
        row = record.to_sheets_row()
        assert row[7] == ""


class TestDiagnosisRecordFromSheetsRow:
    def _roundtrip(self, record: DiagnosisRecord) -> DiagnosisRecord:
        return DiagnosisRecord.from_sheets_row(record.to_sheets_row())

    def test_roundtrip_preserves_data(self):
        original = _sample_record()
        restored = self._roundtrip(original)
        assert restored.vehicle_id == original.vehicle_id
        assert restored.make == original.make
        assert restored.model == original.model
        assert restored.year == original.year
        assert restored.mileage == original.mileage
        assert restored.fault_codes == original.fault_codes
        assert restored.symptoms == original.symptoms
        assert restored.technician == original.technician
        assert restored.ai_diagnosis == original.ai_diagnosis

    def test_short_row_padded_gracefully(self):
        row = ["ID1", "2024-01-01 00:00:00", "ABC123", "Ford", "Focus", "2018", "50000"]
        record = DiagnosisRecord.from_sheets_row(row)
        assert record.fault_codes == []
        assert record.symptoms == ""
        assert record.ai_diagnosis is None

    def test_fault_codes_parsed_correctly(self):
        row = ["", "2024-01-01 00:00:00", "XYZ", "Seat", "Ibiza",
               "2020", "30000", "P0001, P0002, P0003", "", "", "", ""]
        record = DiagnosisRecord.from_sheets_row(row)
        assert record.fault_codes == ["P0001", "P0002", "P0003"]


class TestDiagnosisRecordToDict:
    def test_dict_has_all_keys(self):
        record = _sample_record()
        d = record.to_dict()
        expected_keys = {
            "record_id", "timestamp", "vehicle_id", "make", "model",
            "year", "mileage", "fault_codes", "symptoms", "technician",
            "ai_diagnosis", "ai_recommendations",
        }
        assert set(d.keys()) == expected_keys

    def test_dict_values(self):
        record = _sample_record()
        d = record.to_dict()
        assert d["vehicle_id"] == "1234ABC"
        assert d["fault_codes"] == ["P0301", "P0420"]
        assert d["year"] == 2019
