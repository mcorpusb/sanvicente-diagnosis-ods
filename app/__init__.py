"""Flask application factory."""
import os
import logging

from flask import Flask
from dotenv import load_dotenv

load_dotenv()


def create_app() -> Flask:
    """Create and configure the Flask application."""
    logging.basicConfig(
        level=logging.DEBUG if os.environ.get("FLASK_DEBUG", "True") == "True" else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    app = Flask(__name__, template_folder="templates", static_folder="../static")
    app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    from app.routes import diagnosis_bp, export_bp
    app.register_blueprint(diagnosis_bp)
    app.register_blueprint(export_bp)

    from app.services.sheets_service import ensure_header
    with app.app_context():
        try:
            ensure_header()
        except Exception as exc:  # noqa: BLE001
            app.logger.warning("No se pudo inicializar la cabecera de Sheets: %s", exc)

    return app
