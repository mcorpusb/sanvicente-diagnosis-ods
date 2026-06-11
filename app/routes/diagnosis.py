"""Main dashboard routes."""
import logging
from datetime import datetime

from flask import Blueprint, render_template, request, jsonify, current_app

from app.models.diagnosis import DiagnosisRecord
from app.services.ai_service import get_ai_diagnosis
from app.services.sheets_service import append_record, fetch_all_records

logger = logging.getLogger(__name__)

bp = Blueprint("diagnosis", __name__)


@bp.route("/")
def index():
    """Render the main dashboard page."""
    return render_template("index.html")


@bp.route("/api/diagnose", methods=["POST"])
def diagnose():
    """
    Accept a vehicle diagnosis form submission, call Gemini AI,
    store the result in Google Sheets and return JSON.
    """
    data = request.get_json(force=True)

    required = ["vehicle_id", "make", "model", "year", "mileage", "technician"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Campos requeridos: {', '.join(missing)}"}), 400

    fault_codes = [c.strip() for c in data.get("fault_codes", "").split(",") if c.strip()]
    symptoms = data.get("symptoms", "").strip()

    try:
        year = int(data["year"])
        mileage = int(data["mileage"])
    except (ValueError, TypeError):
        return jsonify({"error": "Año y kilometraje deben ser números enteros."}), 400

    ai_diagnosis, ai_recommendations = get_ai_diagnosis(
        make=data["make"],
        model=data["model"],
        year=year,
        mileage=mileage,
        fault_codes=fault_codes,
        symptoms=symptoms,
    )

    record = DiagnosisRecord(
        vehicle_id=data["vehicle_id"],
        make=data["make"],
        model=data["model"],
        year=year,
        mileage=mileage,
        fault_codes=fault_codes,
        symptoms=symptoms,
        technician=data["technician"],
        ai_diagnosis=ai_diagnosis,
        ai_recommendations=ai_recommendations,
    )

    append_record(record)

    return jsonify(record.to_dict()), 200


@bp.route("/api/records", methods=["GET"])
def list_records():
    """Return all diagnosis records from Google Sheets as JSON."""
    records = fetch_all_records()
    return jsonify([r.to_dict() for r in records]), 200
