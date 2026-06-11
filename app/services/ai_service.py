"""AI diagnosis service using Google Gemini."""
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "Eres un experto mecánico de automoción y técnico de diagnóstico de vehículos. "
    "Tu misión es analizar los códigos de avería OBD-II y los síntomas descritos "
    "para proporcionar un diagnóstico claro y recomendaciones de reparación. "
    "Responde siempre en español, de forma profesional y concisa."
)

_DIAGNOSIS_TEMPLATE = """
Vehículo: {make} {model} ({year}) — {mileage} km
Códigos de avería: {fault_codes}
Síntomas: {symptoms}

Por favor proporciona:
1. DIAGNÓSTICO: Una explicación clara de las posibles causas de los códigos y síntomas.
2. RECOMENDACIONES: Pasos concretos de reparación ordenados por prioridad.
"""


def _build_prompt(make: str, model: str, year: int, mileage: int,
                  fault_codes: list[str], symptoms: str) -> str:
    return _DIAGNOSIS_TEMPLATE.format(
        make=make,
        model=model,
        year=year,
        mileage=mileage,
        fault_codes=", ".join(fault_codes) if fault_codes else "Ninguno",
        symptoms=symptoms or "No se han descrito síntomas adicionales",
    )


def get_ai_diagnosis(make: str, model: str, year: int, mileage: int,
                     fault_codes: list[str], symptoms: str) -> tuple[str, str]:
    """
    Request a diagnosis from Google Gemini.

    Returns a tuple (diagnosis_text, recommendations_text).
    Falls back to a descriptive error string if the API is unavailable.
    """
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key or api_key == "your_gemini_api_key_here":
        logger.warning("GEMINI_API_KEY no configurada; usando diagnóstico de ejemplo.")
        return _mock_diagnosis(fault_codes, symptoms)

    try:
        import google.generativeai as genai  # type: ignore

        genai.configure(api_key=api_key)
        model_obj = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=_SYSTEM_PROMPT,
        )
        prompt = _build_prompt(make, model, year, mileage, fault_codes, symptoms)
        response = model_obj.generate_content(prompt)
        full_text: str = response.text.strip()

        diagnosis, recommendations = _split_response(full_text)
        return diagnosis, recommendations

    except Exception as exc:  # noqa: BLE001
        logger.error("Error al llamar a Gemini API: %s", exc)
        return (
            f"Error al obtener diagnóstico IA: {exc}",
            "Revise la configuración de la API y vuelva a intentarlo.",
        )


def _split_response(text: str) -> tuple[str, str]:
    """Split the AI response into diagnosis and recommendations sections."""
    diagnosis = ""
    recommendations = ""
    current_section = None

    for line in text.splitlines():
        upper = line.upper()
        if "DIAGNÓSTICO" in upper or "DIAGNOSTICO" in upper:
            current_section = "diagnosis"
            tail = line.split(":", 1)[-1].strip() if ":" in line else ""
            if tail:
                diagnosis += tail + "\n"
        elif "RECOMENDACION" in upper or "RECOMENDACIÓN" in upper:
            current_section = "recommendations"
            tail = line.split(":", 1)[-1].strip() if ":" in line else ""
            if tail:
                recommendations += tail + "\n"
        elif current_section == "diagnosis":
            diagnosis += line + "\n"
        elif current_section == "recommendations":
            recommendations += line + "\n"

    if not diagnosis and not recommendations:
        return text, ""
    return diagnosis.strip(), recommendations.strip()


def _mock_diagnosis(fault_codes: list[str], symptoms: str) -> tuple[str, str]:
    """Return a placeholder diagnosis when the API key is not configured."""
    codes_str = ", ".join(fault_codes) if fault_codes else "ningún código registrado"
    diagnosis = (
        f"[MODO DEMO] Se han registrado los siguientes códigos: {codes_str}. "
        "Configure GEMINI_API_KEY en el fichero .env para obtener diagnósticos reales."
    )
    recommendations = (
        "1. Configure su clave de API de Google Gemini en el fichero .env.\n"
        "2. Reinicie la aplicación.\n"
        "3. Vuelva a enviar el formulario de diagnóstico."
    )
    return diagnosis, recommendations
