"""Tests for AI service (mock mode when no API key)."""
import os
import pytest
from unittest.mock import patch, MagicMock

from app.services.ai_service import get_ai_diagnosis, _split_response, _mock_diagnosis


class TestMockDiagnosis:
    def test_returns_tuple(self):
        diagnosis, recommendations = _mock_diagnosis(["P0301"], "Tirones")
        assert isinstance(diagnosis, str)
        assert isinstance(recommendations, str)

    def test_contains_fault_code(self):
        diagnosis, _ = _mock_diagnosis(["P0301"], "")
        assert "P0301" in diagnosis

    def test_no_api_key_triggers_mock(self, monkeypatch):
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        diagnosis, recommendations = get_ai_diagnosis(
            "Toyota", "Corolla", 2020, 50000, ["P0301"], "Tirones"
        )
        assert "MODO DEMO" in diagnosis
        assert isinstance(recommendations, str)

    def test_placeholder_api_key_triggers_mock(self, monkeypatch):
        monkeypatch.setenv("GEMINI_API_KEY", "your_gemini_api_key_here")
        diagnosis, _ = get_ai_diagnosis("Toyota", "Corolla", 2020, 50000, [], "")
        assert "MODO DEMO" in diagnosis


class TestSplitResponse:
    def test_splits_on_diagnostico_header(self):
        text = "DIAGNÓSTICO: Fallo en cilindro 1.\nRECOMENDACIONES: Revisar bujía."
        diag, rec = _split_response(text)
        assert "Fallo en cilindro 1" in diag
        assert "Revisar bujía" in rec

    def test_returns_full_text_when_no_sections(self):
        text = "Texto sin secciones."
        diag, rec = _split_response(text)
        assert diag == text
        assert rec == ""

    def test_multiline_content(self):
        text = (
            "DIAGNÓSTICO:\nProblema A.\nProblema B.\n"
            "RECOMENDACIONES:\n1. Paso uno.\n2. Paso dos."
        )
        diag, rec = _split_response(text)
        assert "Problema A" in diag
        assert "Problema B" in diag
        assert "Paso uno" in rec
        assert "Paso dos" in rec


class TestGetAiDiagnosisWithGemini:
    def test_successful_api_call(self, monkeypatch):
        monkeypatch.setenv("GEMINI_API_KEY", "fake_valid_key")

        mock_response = MagicMock()
        mock_response.text = (
            "DIAGNÓSTICO: El código P0301 indica fallo en el cilindro 1.\n"
            "RECOMENDACIONES: 1. Revisar bujía del cilindro 1."
        )

        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response

        mock_genai = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model

        with patch.dict("sys.modules", {"google.generativeai": mock_genai}):
            diagnosis, recommendations = get_ai_diagnosis(
                "Toyota", "Corolla", 2020, 50000, ["P0301"], "Tirones en aceleración"
            )

        assert "P0301" in diagnosis or "cilindro" in diagnosis
        assert isinstance(recommendations, str)

    def test_api_error_returns_error_string(self, monkeypatch):
        monkeypatch.setenv("GEMINI_API_KEY", "fake_valid_key")

        mock_genai = MagicMock()
        mock_genai.GenerativeModel.side_effect = Exception("Connection error")

        with patch.dict("sys.modules", {"google.generativeai": mock_genai}):
            diagnosis, recommendations = get_ai_diagnosis(
                "Ford", "Focus", 2018, 60000, ["P0420"], "Luz naranja"
            )

        assert "Error" in diagnosis
        assert isinstance(recommendations, str)
