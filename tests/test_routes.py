"""Integration tests for Flask routes."""
import json
import pytest
from unittest.mock import patch, MagicMock

from app import create_app


@pytest.fixture()
def app():
    application = create_app()
    application.config["TESTING"] = True
    yield application


@pytest.fixture()
def client(app):
    return app.test_client()


class TestDiagnoseEndpoint:
    def _post(self, client, payload):
        return client.post(
            "/api/diagnose",
            data=json.dumps(payload),
            content_type="application/json",
        )

    def test_missing_required_fields_returns_400(self, client):
        resp = self._post(client, {"make": "Toyota"})
        assert resp.status_code == 400
        data = resp.get_json()
        assert "error" in data

    def test_invalid_year_returns_400(self, client):
        payload = dict(
            vehicle_id="1234ABC", make="Toyota", model="Corolla",
            year="not-a-number", mileage=50000, technician="Ana"
        )
        resp = self._post(client, payload)
        assert resp.status_code == 400

    @patch("app.routes.diagnosis.append_record")
    @patch("app.routes.diagnosis.get_ai_diagnosis")
    def test_valid_diagnosis_returns_200(self, mock_ai, mock_append, client):
        mock_ai.return_value = ("Diagnóstico de prueba.", "Recomendación de prueba.")
        mock_append.return_value = "TESTID"

        payload = dict(
            vehicle_id="1234ABC", make="Toyota", model="Corolla",
            year=2020, mileage=80000,
            fault_codes="P0301, P0420",
            symptoms="Tirones en aceleración",
            technician="Ana López",
        )
        resp = self._post(client, payload)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["vehicle_id"] == "1234ABC"
        assert data["ai_diagnosis"] == "Diagnóstico de prueba."
        assert data["ai_recommendations"] == "Recomendación de prueba."
        mock_append.assert_called_once()

    @patch("app.routes.diagnosis.append_record")
    @patch("app.routes.diagnosis.get_ai_diagnosis")
    def test_fault_codes_parsed_from_string(self, mock_ai, mock_append, client):
        mock_ai.return_value = ("ok", "ok")
        mock_append.return_value = None

        payload = dict(
            vehicle_id="ABC", make="Seat", model="Ibiza",
            year=2018, mileage=40000, fault_codes="P0001, P0002",
            technician="Juan"
        )
        resp = self._post(client, payload)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["fault_codes"] == ["P0001", "P0002"]


class TestListRecordsEndpoint:
    @patch("app.routes.diagnosis.fetch_all_records")
    def test_returns_json_list(self, mock_fetch, client):
        from app.models.diagnosis import DiagnosisRecord
        from datetime import datetime

        mock_fetch.return_value = [
            DiagnosisRecord(
                vehicle_id="XYZ", make="Ford", model="Focus",
                year=2019, mileage=55000, fault_codes=["P0300"],
                symptoms="Vibración", technician="Pedro",
                ai_diagnosis="Diagnóstico.", ai_recommendations="Recomendaciones.",
                record_id="REC001",
                timestamp=datetime(2024, 1, 1, 12, 0, 0),
            )
        ]

        resp = client.get("/api/records")
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["vehicle_id"] == "XYZ"


class TestIndexRoute:
    def test_index_returns_html(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert b"Dashboard" in resp.data or b"Diagnosis" in resp.data


class TestExportOdsEndpoint:
    @patch("app.routes.export.fetch_all_records")
    def test_returns_ods_content_type(self, mock_fetch, client):
        mock_fetch.return_value = []
        resp = client.get("/api/export/ods")
        assert resp.status_code == 200
        assert "opendocument.spreadsheet" in resp.content_type

    @patch("app.routes.export.fetch_all_records")
    def test_attachment_header_present(self, mock_fetch, client):
        mock_fetch.return_value = []
        resp = client.get("/api/export/ods")
        cd = resp.headers.get("Content-Disposition", "")
        assert "attachment" in cd
        assert ".ods" in cd
