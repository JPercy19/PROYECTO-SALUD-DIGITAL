"""
routes/patients.py - CRUD completo de pacientes (recurso FHIR Patient)

Endpoints:
    GET    /patients          - Lista paginada de pacientes
    POST   /patients          - Crear nuevo paciente
    GET    /patients/<id>     - Obtener un paciente por ID
    PUT    /patients/<id>     - Actualizar paciente
    DELETE /patients/<id>     - Eliminar paciente

Todos requieren autenticación Double API Key.
"""

import uuid
from datetime import date
from flask import Blueprint, request, jsonify
from backend.models import db, Patient
from backend.utils.security import require_api_keys
from backend.utils.validators import validate_patient, parse_pagination
from backend.utils.encryption import encrypt, decrypt


def _parse_date(value) -> date | None:
    """Convierte una cadena ISO (YYYY-MM-DD) a un objeto date, o None si está vacío."""
    if value is None:
        return None
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None

patients_bp = Blueprint("patients", __name__, url_prefix="/patients")


@patients_bp.route("", methods=["GET"])
@require_api_keys
def list_patients():
    """
    Lista pacientes con paginación (limit & offset).

    Query params:
        limit  (int, 1-100, default 20): Número de resultados por página.
        offset (int, default 0):         Desde qué registro empezar.
        name   (str, opcional):          Filtrar por nombre (búsqueda parcial).

    Respuesta:
        {
            "data": [...],
            "total": 42,
            "limit": 20,
            "offset": 0
        }
    """
    limit, offset = parse_pagination(request.args)
    name_filter   = request.args.get("name", "").strip()

    query = Patient.query
    if name_filter:
        query = query.filter(Patient.name.ilike(f"%{name_filter}%"))

    total    = query.count()
    patients = query.order_by(Patient.id).offset(offset).limit(limit).all()

    return jsonify({
        "data":   [p.to_dict() for p in patients],
        "total":  total,
        "limit":  limit,
        "offset": offset,
    }), 200


@patients_bp.route("", methods=["POST"])
@require_api_keys
def create_patient():
    """
    Crea un nuevo paciente.

    Body JSON:
        {
            "name":               "Juan Pérez",           (obligatorio)
            "birth_date":         "1990-05-15",           (YYYY-MM-DD)
            "gender":             "male",
            "identification_doc": "12345678A",            (se encripta)
            "medical_summary":    "Hipertensión leve",    (se encripta)
            "phone":              "+34 600 000 000",
            "email":              "juan@ejemplo.com"
        }
    """
    data   = request.get_json(silent=True) or {}
    errors = validate_patient(data)
    if errors:
        return jsonify({"error": "Datos inválidos", "detail": errors}), 400

    patient = Patient(
        fhir_id            = str(uuid.uuid4()),
        name               = data["name"].strip(),
        birth_date         = _parse_date(data.get("birth_date")),
        gender             = data.get("gender"),
        identification_doc = encrypt(data["identification_doc"])
                             if data.get("identification_doc") else None,
        medical_summary    = encrypt(data["medical_summary"])
                             if data.get("medical_summary") else None,
        phone              = data.get("phone"),
        email              = data.get("email"),
    )
    db.session.add(patient)
    db.session.commit()

    return jsonify({
        "message": "Paciente creado correctamente",
        "patient": patient.to_dict(decrypt_fn=decrypt),
    }), 201


@patients_bp.route("/<int:patient_id>", methods=["GET"])
@require_api_keys
def get_patient(patient_id):
    """Obtiene los datos completos de un paciente por su ID."""
    patient = db.get_or_404(Patient, patient_id)
    return jsonify(patient.to_dict(decrypt_fn=decrypt)), 200


@patients_bp.route("/<int:patient_id>", methods=["PUT"])
@require_api_keys
def update_patient(patient_id):
    """
    Actualiza los datos de un paciente existente.
    Solo se actualizan los campos incluidos en el body.
    """
    patient = db.get_or_404(Patient, patient_id)
    data    = request.get_json(silent=True) or {}

    # Validar solo los campos presentes
    errors = validate_patient({**patient.to_dict(decrypt_fn=decrypt), **data})
    if errors:
        return jsonify({"error": "Datos inválidos", "detail": errors}), 400

    if "name" in data:
        patient.name = data["name"].strip()
    if "birth_date" in data:
        patient.birth_date = _parse_date(data["birth_date"])
    if "gender" in data:
        patient.gender = data["gender"]
    if "identification_doc" in data:
        patient.identification_doc = (
            encrypt(data["identification_doc"]) if data["identification_doc"] else None
        )
    if "medical_summary" in data:
        patient.medical_summary = (
            encrypt(data["medical_summary"]) if data["medical_summary"] else None
        )
    if "phone" in data:
        patient.phone = data["phone"]
    if "email" in data:
        patient.email = data["email"]

    db.session.commit()

    return jsonify({
        "message": "Paciente actualizado correctamente",
        "patient": patient.to_dict(decrypt_fn=decrypt),
    }), 200


@patients_bp.route("/<int:patient_id>", methods=["DELETE"])
@require_api_keys
def delete_patient(patient_id):
    """Elimina un paciente y todas sus observaciones (CASCADE)."""
    patient = db.get_or_404(Patient, patient_id)
    db.session.delete(patient)
    db.session.commit()
    return jsonify({"message": f"Paciente {patient_id} eliminado correctamente"}), 200


@patients_bp.route("/<int:patient_id>/fhir", methods=["GET"])
@require_api_keys
def get_patient_fhir(patient_id):
    """Devuelve el paciente en formato FHIR R4."""
    patient = db.get_or_404(Patient, patient_id)
    return jsonify(patient.to_fhir()), 200
