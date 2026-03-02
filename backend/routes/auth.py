"""
routes/auth.py - Endpoints de autenticación Double API Key

Endpoints:
    POST /auth/verify   - Verifica que las API keys sean válidas
    POST /auth/users    - Crea un nuevo usuario (solo admin)
"""

from flask import Blueprint, request, jsonify
from backend.models import db, User
from backend.utils.security import require_api_keys

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/verify", methods=["POST"])
def verify_keys():
    """
    Verifica que las API keys sean válidas.

    Cabeceras requeridas:
        X-Access-Key:     Clave de acceso del usuario
        X-Permission-Key: Clave de permiso del usuario

    Respuesta exitosa (200):
        { "authenticated": true, "username": "..." }
    """
    access_key     = request.headers.get("X-Access-Key", "")
    permission_key = request.headers.get("X-Permission-Key", "")

    if not access_key or not permission_key:
        return jsonify({
            "authenticated": False,
            "error": "Se requieren las cabeceras X-Access-Key y X-Permission-Key",
        }), 401

    user = User.query.filter_by(
        access_key=access_key,
        permission_key=permission_key,
        is_active=True,
    ).first()

    if not user:
        return jsonify({"authenticated": False, "error": "Credenciales inválidas"}), 401

    return jsonify({"authenticated": True, "username": user.username}), 200


@auth_bp.route("/users", methods=["POST"])
@require_api_keys
def create_user():
    """
    Crea un nuevo usuario con sus API keys. Requiere autenticación.

    Body JSON:
        {
            "username":       "nuevo_usuario",
            "access_key":     "nueva-access-key",
            "permission_key": "nueva-permission-key"
        }
    """
    data = request.get_json(silent=True) or {}

    username       = data.get("username", "").strip()
    access_key     = data.get("access_key", "").strip()
    permission_key = data.get("permission_key", "").strip()

    if not username or not access_key or not permission_key:
        return jsonify({
            "error": "Se requieren los campos: username, access_key, permission_key"
        }), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": f"El usuario '{username}' ya existe"}), 409

    new_user = User(
        username=username,
        access_key=access_key,
        permission_key=permission_key,
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": f"Usuario '{username}' creado correctamente",
        "user": new_user.to_dict(),
    }), 201
