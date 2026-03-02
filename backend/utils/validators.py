"""
utils/validators.py - Validaciones de datos FHIR y de entrada general

Valida los datos recibidos en los endpoints antes de guardarlos en la BD.
"""

from datetime import date


# Valores permitidos por FHIR R4 para el género del paciente
VALID_GENDERS = {"male", "female", "other", "unknown"}

# Valores permitidos por FHIR R4 para el estado de una observación
VALID_OBS_STATUSES = {"registered", "preliminary", "final", "amended", "cancelled"}


def validate_patient(data: dict) -> list[str]:
    """
    Valida los datos de un paciente.

    Args:
        data: Diccionario con los campos del paciente.

    Returns:
        Lista de errores encontrados. Lista vacía = datos válidos.
    """
    errors = []

    # Campo obligatorio
    if not data.get("name", "").strip():
        errors.append("El campo 'name' es obligatorio y no puede estar vacío.")

    # Validar género (si se proporciona)
    gender = data.get("gender")
    if gender and gender not in VALID_GENDERS:
        errors.append(
            f"El campo 'gender' debe ser uno de: {', '.join(sorted(VALID_GENDERS))}."
        )

    # Validar fecha de nacimiento (si se proporciona)
    birth_date = data.get("birth_date")
    if birth_date:
        try:
            parsed = date.fromisoformat(str(birth_date))
            if parsed > date.today():
                errors.append("El campo 'birth_date' no puede ser una fecha futura.")
        except ValueError:
            errors.append(
                "El campo 'birth_date' debe tener el formato ISO 8601 (YYYY-MM-DD)."
            )

    # Validar email básico (si se proporciona)
    email = data.get("email", "")
    if email and "@" not in email:
        errors.append("El campo 'email' no tiene un formato válido.")

    return errors


def validate_observation(data: dict) -> list[str]:
    """
    Valida los datos de una observación clínica.

    Args:
        data: Diccionario con los campos de la observación.

    Returns:
        Lista de errores encontrados. Lista vacía = datos válidos.
    """
    errors = []

    # Campos obligatorios
    if not data.get("patient_id"):
        errors.append("El campo 'patient_id' es obligatorio.")

    if not data.get("code", "").strip():
        errors.append("El campo 'code' es obligatorio (código LOINC/SNOMED).")

    # Validar estado (si se proporciona)
    status = data.get("status")
    if status and status not in VALID_OBS_STATUSES:
        errors.append(
            f"El campo 'status' debe ser uno de: {', '.join(sorted(VALID_OBS_STATUSES))}."
        )

    # Validar que el valor sea numérico (si se proporciona)
    value = data.get("value")
    if value is not None:
        try:
            float(value)
        except (TypeError, ValueError):
            errors.append("El campo 'value' debe ser un número.")

    # Validar coherencia del rango de referencia
    ref_low  = data.get("ref_low")
    ref_high = data.get("ref_high")
    if ref_low is not None and ref_high is not None:
        try:
            if float(ref_low) >= float(ref_high):
                errors.append(
                    "El campo 'ref_low' debe ser menor que 'ref_high'."
                )
        except (TypeError, ValueError):
            errors.append("Los campos 'ref_low' y 'ref_high' deben ser números.")

    return errors


def parse_pagination(args: dict) -> tuple[int, int]:
    """
    Extrae y valida los parámetros de paginación limit y offset.

    Args:
        args: Parámetros de la query string (request.args).

    Returns:
        Tupla (limit, offset) con valores enteros válidos.
    """
    try:
        limit = max(1, min(int(args.get("limit", 20)), 100))
    except (TypeError, ValueError):
        limit = 20

    try:
        offset = max(0, int(args.get("offset", 0)))
    except (TypeError, ValueError):
        offset = 0

    return limit, offset
