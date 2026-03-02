"""
models.py - Modelos SQLAlchemy para la base de datos Salud Digital

Cada clase representa una tabla en PostgreSQL.
Los campos sensibles (identification_doc, medical_summary) se almacenan
encriptados mediante Fernet (ver utils/encryption.py).
"""

from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

# Instancia compartida de SQLAlchemy (se inicializa en app.py)
db = SQLAlchemy()


class User(db.Model):
    """
    Tabla: users
    Almacena las credenciales de autenticación Double API Key.
    """
    __tablename__ = "users"

    id             = db.Column(db.Integer, primary_key=True)
    username       = db.Column(db.String(100), unique=True, nullable=False)
    # Las API keys se guardan tal cual; en producción usar hashes
    access_key     = db.Column(db.String(255), nullable=False)
    permission_key = db.Column(db.String(255), nullable=False)
    is_active      = db.Column(db.Boolean, default=True)
    created_at     = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self):
        """Devuelve representación segura (sin las keys)."""
        return {
            "id": self.id,
            "username": self.username,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Patient(db.Model):
    """
    Tabla: patients
    Recurso FHIR Patient con campos sensibles encriptados.
    """
    __tablename__ = "patients"

    id                 = db.Column(db.Integer, primary_key=True)
    fhir_id            = db.Column(db.String(100), unique=True)
    name               = db.Column(db.String(255), nullable=False)
    birth_date         = db.Column(db.Date)
    gender             = db.Column(db.String(20))
    # Almacenados encriptados con Fernet
    identification_doc = db.Column(db.Text)
    medical_summary    = db.Column(db.Text)
    # Contacto
    phone              = db.Column(db.String(50))
    email              = db.Column(db.String(255))
    # Auditoría
    created_at         = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at         = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relación con observaciones (one-to-many)
    observations = db.relationship(
        "Observation", back_populates="patient", cascade="all, delete-orphan"
    )

    def to_dict(self, decrypt_fn=None):
        """
        Devuelve el paciente como diccionario.
        Si se pasa decrypt_fn, desencripta los campos sensibles.
        """
        return {
            "id": self.id,
            "fhir_id": self.fhir_id,
            "name": self.name,
            "birth_date": self.birth_date.isoformat() if self.birth_date else None,
            "gender": self.gender,
            "identification_doc": (
                decrypt_fn(self.identification_doc)
                if decrypt_fn and self.identification_doc
                else "***"
            ),
            "medical_summary": (
                decrypt_fn(self.medical_summary)
                if decrypt_fn and self.medical_summary
                else "***"
            ),
            "phone": self.phone,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def to_fhir(self, decrypt_fn=None):
        """Devuelve el recurso en formato FHIR R4 Patient."""
        resource = {
            "resourceType": "Patient",
            "id": self.fhir_id,
            "name": [{"use": "official", "text": self.name}],
            "gender": self.gender,
        }
        if self.birth_date:
            resource["birthDate"] = self.birth_date.isoformat()
        if self.phone:
            resource["telecom"] = [{"system": "phone", "value": self.phone}]
        if self.email:
            resource.setdefault("telecom", []).append(
                {"system": "email", "value": self.email}
            )
        return resource


class Observation(db.Model):
    """
    Tabla: observations
    Recurso FHIR Observation para mediciones clínicas.
    """
    __tablename__ = "observations"

    id             = db.Column(db.Integer, primary_key=True)
    patient_id     = db.Column(
        db.Integer, db.ForeignKey("patients.id", ondelete="CASCADE"), nullable=False
    )
    fhir_id        = db.Column(db.String(100), unique=True)
    code           = db.Column(db.String(100), nullable=False)
    display        = db.Column(db.String(255))
    value          = db.Column(db.Numeric(10, 4))
    unit           = db.Column(db.String(50))
    # Rango de referencia para detección de outliers
    ref_low        = db.Column(db.Numeric(10, 4))
    ref_high       = db.Column(db.Numeric(10, 4))
    status         = db.Column(db.String(50), default="final")
    effective_date = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    created_at     = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relación inversa con Patient
    patient = db.relationship("Patient", back_populates="observations")

    @property
    def is_outlier(self):
        """Devuelve True si el valor está fuera del rango de referencia."""
        if self.value is None:
            return False
        if self.ref_low is not None and float(self.value) < float(self.ref_low):
            return True
        if self.ref_high is not None and float(self.value) > float(self.ref_high):
            return True
        return False

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "fhir_id": self.fhir_id,
            "code": self.code,
            "display": self.display,
            "value": float(self.value) if self.value is not None else None,
            "unit": self.unit,
            "ref_low": float(self.ref_low) if self.ref_low is not None else None,
            "ref_high": float(self.ref_high) if self.ref_high is not None else None,
            "status": self.status,
            "is_outlier": self.is_outlier,
            "effective_date": (
                self.effective_date.isoformat() if self.effective_date else None
            ),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def to_fhir(self):
        """Devuelve el recurso en formato FHIR R4 Observation."""
        return {
            "resourceType": "Observation",
            "id": self.fhir_id,
            "status": self.status,
            "code": {
                "coding": [{"code": self.code, "display": self.display}]
            },
            "subject": {"reference": f"Patient/{self.patient.fhir_id}"},
            "effectiveDateTime": (
                self.effective_date.isoformat() if self.effective_date else None
            ),
            "valueQuantity": {
                "value": float(self.value) if self.value is not None else None,
                "unit": self.unit,
            },
        }
