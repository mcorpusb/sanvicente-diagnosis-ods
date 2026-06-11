"""Vehicle diagnosis data model."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class DiagnosisRecord:
    """Represents a single vehicle diagnosis record."""

    vehicle_id: str
    make: str
    model: str
    year: int
    mileage: int
    fault_codes: list[str]
    symptoms: str
    technician: str
    ai_diagnosis: Optional[str] = None
    ai_recommendations: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    record_id: Optional[str] = None

    def to_sheets_row(self) -> list:
        """Convert record to a flat list suitable for Google Sheets."""
        return [
            self.record_id or "",
            self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            self.vehicle_id,
            self.make,
            self.model,
            str(self.year),
            str(self.mileage),
            ", ".join(self.fault_codes),
            self.symptoms,
            self.technician,
            self.ai_diagnosis or "",
            self.ai_recommendations or "",
        ]

    @classmethod
    def from_sheets_row(cls, row: list) -> "DiagnosisRecord":
        """Build a DiagnosisRecord from a Google Sheets row."""
        while len(row) < 12:
            row.append("")
        return cls(
            record_id=row[0] or None,
            timestamp=datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S") if row[1] else datetime.now(),
            vehicle_id=row[2],
            make=row[3],
            model=row[4],
            year=int(row[5]) if row[5] else 0,
            mileage=int(row[6]) if row[6] else 0,
            fault_codes=[c.strip() for c in row[7].split(",") if c.strip()],
            symptoms=row[8],
            technician=row[9],
            ai_diagnosis=row[10] or None,
            ai_recommendations=row[11] or None,
        )

    def to_dict(self) -> dict:
        """Serialize to a JSON-friendly dictionary."""
        return {
            "record_id": self.record_id,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "vehicle_id": self.vehicle_id,
            "make": self.make,
            "model": self.model,
            "year": self.year,
            "mileage": self.mileage,
            "fault_codes": self.fault_codes,
            "symptoms": self.symptoms,
            "technician": self.technician,
            "ai_diagnosis": self.ai_diagnosis,
            "ai_recommendations": self.ai_recommendations,
        }


SHEETS_HEADER = [
    "ID",
    "Fecha/Hora",
    "Matrícula",
    "Marca",
    "Modelo",
    "Año",
    "Kilometraje",
    "Códigos de avería",
    "Síntomas",
    "Técnico",
    "Diagnóstico IA",
    "Recomendaciones IA",
]
