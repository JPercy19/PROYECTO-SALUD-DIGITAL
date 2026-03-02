"""
routes/observations.py - CRUD de observaciones clínicas (recurso FHIR Observation)

Endpoints:
    GET    /observations                     - Lista paginada de observaciones
    POST   /observations                     - Crear nueva observación
    GET    /observations/<id>                - Obtener observación por ID
    DELETE /observations/<id>                - Eliminar observación
    GET    /patients/<id>/observations       - Observaciones de un paciente

Todos requieren autenticación Double API Key.
"""

import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify
from backend.models import db, Observation, Patient
from backend.utils.security import require_api_keys
from backend.utils.validators import validate_observation, parse_pagination


def _parse_datetime(value) -> datetime | None:
    """Convierte una cadena ISO a datetime, o None si está vacío."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value))
    except ValueError:
        return None

observations_bp = Blueprint("observations", __name__)


@observations_bp.route("/observations", methods=["GET"])
@require_api_keys
def list_observations():
    """
    Lista observaciones con paginación.

    Query params:
        limit   (int, 1-100, default 20)
        offset  (int, default 0)
        code    (str, opcional): Filtrar por código LOINC/SNOMED.
    """
    limit, offset = parse_pagination(request.args)
    code_filter   = request.args.get("code", "").strip()

    query = Observation.query
    if code_filter:
        query = query.filter(Observation.code.ilike(f"%{code_filter}%"))

    total        = query.count()
    observations = (
        query.order_by(Observation.effective_date.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return jsonify({
        "data":   [o.to_dict() for o in observations],
        "total":  total,
        "limit":  limit,
        "offset": offset,
    }), 200


@observations_bp.route("/observations", methods=["POST"])
@require_api_keys
def create_observation():
    """
    Crea una nueva observación clínica.

    Body JSON:
        {
            "patient_id":     1,              (obligatorio)
            "code":           "8867-4",       (obligatorio, LOINC)
            "display":        "Heart rate",
            "value":          72.0,
            "unit":           "beats/min",
            "ref_low":        60.0,
            "ref_high":       100.0,
            "status":         "final",
            "effective_date": "2024-01-15T10:30:00"
        }
    """
    data   = request.get_json(silent=True) or {}
    errors = validate_observation(data)
    if errors:
        return jsonify({"error": "Datos inválidos", "detail": errors}), 400

    # Verificar que el paciente existe
    patient = db.session.get(Patient, data["patient_id"])
    if not patient:
        return jsonify({"error": f"Paciente {data['patient_id']} no encontrado"}), 404

    observation = Observation(
        fhir_id        = str(uuid.uuid4()),
        patient_id     = data["patient_id"],
        code           = data["code"].strip(),
        display        = data.get("display"),
        value          = data.get("value"),
        unit           = data.get("unit"),
        ref_low        = data.get("ref_low"),
        ref_high       = data.get("ref_high"),
        status         = data.get("status", "final"),
        effective_date = _parse_datetime(data.get("effective_date")),
    )
    db.session.add(observation)
    db.session.commit()

    return jsonify({
        "message":     "Observación creada correctamente",
        "observation": observation.to_dict(),
    }), 201


@observations_bp.route("/observations/<int:obs_id>", methods=["GET"])
@require_api_keys
def get_observation(obs_id):
    """Obtiene una observación por su ID."""
    obs = db.get_or_404(Observation, obs_id)
    return jsonify(obs.to_dict()), 200


@observations_bp.route("/observations/<int:obs_id>", methods=["DELETE"])
@require_api_keys
def delete_observation(obs_id):
    """Elimina una observación."""
    obs = db.get_or_404(Observation, obs_id)
    db.session.delete(obs)
    db.session.commit()
    return jsonify({"message": f"Observación {obs_id} eliminada correctamente"}), 200


@observations_bp.route("/observations/<int:obs_id>/fhir", methods=["GET"])
@require_api_keys
def get_observation_fhir(obs_id):
    """Devuelve la observación en formato FHIR R4."""
    obs = db.get_or_404(Observation, obs_id)
    return jsonify(obs.to_fhir()), 200


@observations_bp.route("/patients/<int:patient_id>/observations", methods=["GET"])
@require_api_keys
def get_patient_observations(patient_id):
    """
    Obtiene todas las observaciones de un paciente con paginación.

    Query params:
        limit  (int, 1-100, default 20)
        offset (int, default 0)
        code   (str, opcional): Filtrar por código.
    """
    # Verificar que el paciente existe
    db.get_or_404(Patient, patient_id)

    limit, offset = parse_pagination(request.args)
    code_filter   = request.args.get("code", "").strip()

    query = Observation.query.filter_by(patient_id=patient_id)
    if code_filter:
        query = query.filter(Observation.code.ilike(f"%{code_filter}%"))

    total        = query.count()
    observations = (
        query.order_by(Observation.effective_date.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return jsonify({
        "data":       [o.to_dict() for o in observations],
        "total":      total,
        "limit":      limit,
        "offset":     offset,
        "patient_id": patient_id,
    }), 200
