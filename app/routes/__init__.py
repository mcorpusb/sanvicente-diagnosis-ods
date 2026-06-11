"""Package init for routes."""
from .diagnosis import bp as diagnosis_bp
from .export import bp as export_bp

__all__ = ["diagnosis_bp", "export_bp"]
