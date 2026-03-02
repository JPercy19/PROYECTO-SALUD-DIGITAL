"""
app.py - API REST principal del Proyecto Salud Digital

Arranca el servidor Flask, inicializa la base de datos y registra
todos los blueprints (rutas) de la API.

Uso rápido:
    python backend/app.py

Con Gunicorn (producción):
    gunicorn -w 4 -b 0.0.0.0:5000 "backend.app:create_app()"
"""

import os
import sys

# Agregar el directorio raíz del proyecto al path de Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from backend.config import active_config
from backend.models import db

# Blueprints de rutas
from backend.routes.auth import auth_bp
from backend.routes.patients import patients_bp
from backend.routes.observations import observations_bp


def create_app(config=None) -> Flask:
    """
    Fábrica de la aplicación Flask (Application Factory Pattern).
    Recibe una configuración opcional para facilitar los tests.
    """
    app = Flask(__name__)
    app.config.from_object(config or active_config)

    # ------------------------------------------------------------------
    # CORS: permite peticiones desde el frontend Streamlit
    # ------------------------------------------------------------------
    CORS(app)

    # ------------------------------------------------------------------
    # Rate Limiting: Anti-DoS (100 peticiones/minuto por IP por defecto)
    # ------------------------------------------------------------------
    Limiter(
        get_remote_address,
        app=app,
        default_limits=[app.config.get("RATELIMIT_DEFAULT", "100 per minute")],
        storage_uri=app.config.get("RATELIMIT_STORAGE_URL", "memory://"),
    )

    # ------------------------------------------------------------------
    # Base de datos SQLAlchemy
    # ------------------------------------------------------------------
    db.init_app(app)
    with app.app_context():
        db.create_all()   # Crea las tablas si no existen

    # ------------------------------------------------------------------
    # Registrar blueprints (grupos de rutas)
    # ------------------------------------------------------------------
    app.register_blueprint(auth_bp)
    app.register_blueprint(patients_bp)
    app.register_blueprint(observations_bp)

    # ------------------------------------------------------------------
    # Ruta raíz: comprobación de estado (health check)
    # ------------------------------------------------------------------
    @app.route("/")
    def health_check():
        return jsonify({
            "status":  "ok",
            "service": "Salud Digital API",
            "version": "1.0.0",
        }), 200

    # ------------------------------------------------------------------
    # Manejadores de errores globales
    # ------------------------------------------------------------------
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Recurso no encontrado"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Método HTTP no permitido"}), 405

    @app.errorhandler(429)
    def too_many_requests(e):
        return jsonify({
            "error": "Demasiadas peticiones",
            "detail": "Has superado el límite de peticiones. Espera un momento.",
        }), 429

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"error": "Error interno del servidor"}), 500

    return app


# Punto de entrada al ejecutar directamente: python backend/app.py
if __name__ == "__main__":
    port = int(os.environ.get("BACKEND_PORT", 5000))
    app  = create_app()
    print(f"🚀 Salud Digital API escuchando en http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=active_config.DEBUG)
