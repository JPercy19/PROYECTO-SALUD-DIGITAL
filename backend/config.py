"""
config.py - Configuración centralizada del proyecto Salud Digital
Lee todas las variables desde el archivo .env
"""

import os
from dotenv import load_dotenv

# Cargar variables del archivo .env (si existe)
load_dotenv()


class Config:
    """Configuración base compartida por todos los entornos."""

    # ------------------------------------------------------------------
    # Base de datos
    # ------------------------------------------------------------------
    # Formato: postgresql://usuario:contraseña@host:puerto/nombre_db
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/salud_digital",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Reduce overhead de memoria

    # ------------------------------------------------------------------
    # Flask
    # ------------------------------------------------------------------
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "")
    if not SECRET_KEY and os.environ.get("FLASK_ENV") == "production":
        raise ValueError(
            "La variable FLASK_SECRET_KEY debe estar configurada en producción."
        )
    SECRET_KEY = SECRET_KEY or "clave-secreta-dev-cambiar"

    # ------------------------------------------------------------------
    # Encriptación (Fernet)
    # Generar una clave nueva:
    #   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    # ------------------------------------------------------------------
    ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY", "")

    # ------------------------------------------------------------------
    # Rate Limiting (protección Anti-DoS)
    # ------------------------------------------------------------------
    RATELIMIT_DEFAULT = "100 per minute"
    RATELIMIT_STORAGE_URL = os.environ.get("RATELIMIT_STORAGE_URL", "memory://")

    # ------------------------------------------------------------------
    # API Keys de administrador
    # ------------------------------------------------------------------
    ADMIN_ACCESS_KEY = os.environ.get(
        "ADMIN_ACCESS_KEY", "admin-access-key-cambiar-en-produccion"
    )
    ADMIN_PERMISSION_KEY = os.environ.get(
        "ADMIN_PERMISSION_KEY", "admin-permission-key-cambiar-en-produccion"
    )


class DevelopmentConfig(Config):
    """Configuración para desarrollo local."""
    DEBUG = True


class ProductionConfig(Config):
    """Configuración para producción."""
    DEBUG = False
    RATELIMIT_DEFAULT = "60 per minute"


# Mapa de entornos disponibles
config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}

# Seleccionar la configuración según la variable de entorno FLASK_ENV
active_config = config_map.get(
    os.environ.get("FLASK_ENV", "development"),
    DevelopmentConfig,
)
