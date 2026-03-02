"""
utils/security.py - Autenticación Double API Key y protección Anti-DoS

La API requiere DOS cabeceras en cada petición:
    X-Access-Key:     Identifica quién hace la petición.
    X-Permission-Key: Autoriza el acceso (segunda capa de seguridad).

Ambas claves deben coincidir con las almacenadas en la tabla 'users'.
"""

import os
from functools import wraps
from flask import request, jsonify, current_app


def require_api_keys(f):
    """
    Decorador que verifica la autenticación Double API Key.

    Uso:
        @app.route("/ruta")
        @require_api_keys
        def mi_endpoint():
            ...

    Responde con HTTP 401 si alguna clave falta o es incorrecta.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        access_key     = request.headers.get("X-Access-Key", "")
        permission_key = request.headers.get("X-Permission-Key", "")

        if not access_key or not permission_key:
            return jsonify({
                "error": "Autenticación requerida",
                "detail": "Se requieren las cabeceras X-Access-Key y X-Permission-Key",
            }), 401

        # Verificar contra la BD (importación local para evitar circular)
        from backend.models import User, db

        user = User.query.filter_by(
            access_key=access_key,
            permission_key=permission_key,
            is_active=True,
        ).first()

        if not user:
            return jsonify({
                "error": "Credenciales inválidas",
                "detail": "Las API keys proporcionadas no son correctas o el usuario está inactivo",
            }), 401

        return f(*args, **kwargs)

    return decorated
