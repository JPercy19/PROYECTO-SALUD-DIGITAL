"""
demo.py - Inicio rápido SIN configuración (no requiere PostgreSQL)
=================================================================

Este script arranca toda la aplicación con un solo comando:

    python demo.py

Qué hace automáticamente:
  1. Genera una clave de encriptación.
  2. Crea una base de datos SQLite local (demo_salud_digital.db).
  3. Inserta pacientes y observaciones de ejemplo.
  4. Inicia el backend Flask en http://localhost:5000.
  5. Inicia el frontend Streamlit en http://localhost:8501.
  6. Muestra las credenciales de acceso en pantalla.

Para detener todo: Ctrl + C
"""

import os
import sys
import time
import uuid
import threading
import subprocess
from datetime import date, datetime, timezone

# ────────────────────────────────────────────────────────────────────────────
# 1. Configurar variables de entorno ANTES de importar Flask/SQLAlchemy
# ────────────────────────────────────────────────────────────────────────────
from cryptography.fernet import Fernet

DEMO_ACCESS_KEY     = "demo-access-key"
DEMO_PERMISSION_KEY = "demo-permission-key"
ENCRYPTION_KEY      = Fernet.generate_key().decode()

os.environ.update({
    "DATABASE_URL":          "sqlite:///demo_salud_digital.db",
    "ENCRYPTION_KEY":        ENCRYPTION_KEY,
    "ADMIN_ACCESS_KEY":      DEMO_ACCESS_KEY,
    "ADMIN_PERMISSION_KEY":  DEMO_PERMISSION_KEY,
    "FLASK_SECRET_KEY":      "demo-secret-not-for-production",
    "FLASK_ENV":             "development",
    "BACKEND_URL":           "http://localhost:5000",
    "RATELIMIT_STORAGE_URL": "memory://",
})

# ────────────────────────────────────────────────────────────────────────────
# 2. Crear la app Flask con SQLite (sin necesidad de PostgreSQL)
# ────────────────────────────────────────────────────────────────────────────
from backend.app import create_app
from backend.config import DevelopmentConfig
from backend.models import db, User, Patient, Observation
from backend.utils.encryption import encrypt


class DemoConfig(DevelopmentConfig):
    """Configuración de demostración: SQLite, sin rate limiting."""
    SQLALCHEMY_DATABASE_URI = "sqlite:///demo_salud_digital.db"
    RATELIMIT_ENABLED       = False


app = create_app(DemoConfig)


# ────────────────────────────────────────────────────────────────────────────
# 3. Datos de ejemplo (pacientes y observaciones clínicas)
# ────────────────────────────────────────────────────────────────────────────
def seed_demo_data():
    """Inserta datos de ejemplo si la base de datos está vacía."""
    with app.app_context():

        # Usuario demo
        if not User.query.filter_by(username="demo").first():
            db.session.add(User(
                username="demo",
                access_key=DEMO_ACCESS_KEY,
                permission_key=DEMO_PERMISSION_KEY,
            ))

        # Pacientes con observaciones
        if Patient.query.count() == 0:
            demo_patients = [
                {
                    "name":               "María García López",
                    "birth_date":         date(1985, 3, 20),
                    "gender":             "female",
                    "identification_doc": "12345678A",
                    "medical_summary":    "Hipertensión arterial leve. Alergia a la penicilina.",
                    "phone":              "+34 600 111 222",
                    "email":              "maria.garcia@ejemplo.com",
                    "observations": [
                        # Presión sistólica — 1er valor es outlier (>140)
                        dict(code="8480-6", display="Presión sistólica",
                             value=148.0, unit="mmHg", ref_low=90.0, ref_high=140.0,
                             days_ago=30),
                        dict(code="8480-6", display="Presión sistólica",
                             value=135.0, unit="mmHg", ref_low=90.0, ref_high=140.0,
                             days_ago=20),
                        dict(code="8480-6", display="Presión sistólica",
                             value=128.0, unit="mmHg", ref_low=90.0, ref_high=140.0,
                             days_ago=10),
                        dict(code="8480-6", display="Presión sistólica",
                             value=122.0, unit="mmHg", ref_low=90.0, ref_high=140.0,
                             days_ago=1),
                        dict(code="2093-3", display="Colesterol total",
                             value=215.0, unit="mg/dL", ref_low=0.0, ref_high=200.0,
                             days_ago=15),
                    ],
                },
                {
                    "name":               "Carlos Martínez Ruiz",
                    "birth_date":         date(1972, 7, 15),
                    "gender":             "male",
                    "identification_doc": "87654321B",
                    "medical_summary":    "Diabetes tipo 2. Control glucémico en seguimiento.",
                    "phone":              "+34 600 333 444",
                    "email":              "carlos.martinez@ejemplo.com",
                    "observations": [
                        dict(code="2345-7", display="Glucosa en sangre",
                             value=145.0, unit="mg/dL", ref_low=70.0, ref_high=110.0,
                             days_ago=45),
                        dict(code="2345-7", display="Glucosa en sangre",
                             value=128.0, unit="mg/dL", ref_low=70.0, ref_high=110.0,
                             days_ago=30),
                        dict(code="2345-7", display="Glucosa en sangre",
                             value=118.0, unit="mg/dL", ref_low=70.0, ref_high=110.0,
                             days_ago=15),
                        dict(code="2345-7", display="Glucosa en sangre",
                             value=105.0, unit="mg/dL", ref_low=70.0, ref_high=110.0,
                             days_ago=1),
                        dict(code="8867-4", display="Frecuencia cardíaca",
                             value=88.0, unit="lpm", ref_low=60.0, ref_high=100.0,
                             days_ago=5),
                    ],
                },
                {
                    "name":               "Ana Torres Vega",
                    "birth_date":         date(1995, 11, 5),
                    "gender":             "female",
                    "identification_doc": "11223344C",
                    "medical_summary":    "Paciente sana. Revisión anual.",
                    "phone":              "+34 600 555 666",
                    "email":              "ana.torres@ejemplo.com",
                    "observations": [
                        dict(code="8867-4", display="Frecuencia cardíaca",
                             value=72.0, unit="lpm", ref_low=60.0, ref_high=100.0,
                             days_ago=10),
                        dict(code="29463-7", display="Peso corporal",
                             value=65.5, unit="kg", ref_low=45.0, ref_high=90.0,
                             days_ago=10),
                        dict(code="8302-2", display="Talla",
                             value=165.0, unit="cm", days_ago=10),
                    ],
                },
                {
                    "name":               "Roberto Sánchez Pérez",
                    "birth_date":         date(1960, 5, 22),
                    "gender":             "male",
                    "identification_doc": "55667788D",
                    "medical_summary":    "Insuficiencia cardíaca leve. Seguimiento cardiológico.",
                    "phone":              "+34 600 777 888",
                    "email":              "roberto.sanchez@ejemplo.com",
                    "observations": [
                        dict(code="8867-4", display="Frecuencia cardíaca",
                             value=110.0, unit="lpm", ref_low=60.0, ref_high=100.0,
                             days_ago=20),
                        dict(code="8867-4", display="Frecuencia cardíaca",
                             value=98.0, unit="lpm", ref_low=60.0, ref_high=100.0,
                             days_ago=10),
                        dict(code="8480-6", display="Presión sistólica",
                             value=155.0, unit="mmHg", ref_low=90.0, ref_high=140.0,
                             days_ago=20),
                        dict(code="8480-6", display="Presión sistólica",
                             value=142.0, unit="mmHg", ref_low=90.0, ref_high=140.0,
                             days_ago=5),
                    ],
                },
            ]

            from datetime import timedelta
            today = datetime.now(timezone.utc)

            for p_data in demo_patients:
                obs_list = p_data.pop("observations", [])
                patient = Patient(
                    fhir_id            = str(uuid.uuid4()),
                    name               = p_data["name"],
                    birth_date         = p_data["birth_date"],
                    gender             = p_data["gender"],
                    identification_doc = encrypt(p_data["identification_doc"]),
                    medical_summary    = encrypt(p_data["medical_summary"]),
                    phone              = p_data["phone"],
                    email              = p_data["email"],
                )
                db.session.add(patient)
                db.session.flush()  # obtener patient.id antes del commit

                for obs in obs_list:
                    days_ago = obs.pop("days_ago", 0)
                    db.session.add(Observation(
                        fhir_id        = str(uuid.uuid4()),
                        patient_id     = patient.id,
                        status         = "final",
                        effective_date = today - timedelta(days=days_ago),
                        **obs,
                    ))

            db.session.commit()
            print("✅ Base de datos de demo creada con 4 pacientes y 18 observaciones.")
        else:
            print("✅ Base de datos de demo ya existía.")


# ────────────────────────────────────────────────────────────────────────────
# 4. Arrancar el backend Flask en un hilo en segundo plano
# ────────────────────────────────────────────────────────────────────────────
def run_backend():
    """Corre Flask sin el reloader para que funcione en un hilo."""
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)


# ────────────────────────────────────────────────────────────────────────────
# 5. Punto de entrada principal
# ────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":

    print()
    print("=" * 58)
    print("   🏥  SALUD DIGITAL — INICIO RÁPIDO DE DEMO")
    print("=" * 58)

    # Sembrar datos y arrancar backend
    print("\n▶ Preparando base de datos SQLite...")
    seed_demo_data()

    print("▶ Iniciando servidor backend (Flask)...")
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()
    time.sleep(2)   # esperar a que Flask esté listo
    print("✅ Backend listo en http://localhost:5000\n")

    # Mostrar credenciales de acceso
    print("  Credenciales para iniciar sesión en el dashboard:")
    print("  ┌" + "─" * 50 + "┐")
    print(f"  │  X-Access-Key:     {DEMO_ACCESS_KEY:<30}│")
    print(f"  │  X-Permission-Key: {DEMO_PERMISSION_KEY:<30}│")
    print("  └" + "─" * 50 + "┘")
    print()
    print("▶ Iniciando frontend Streamlit...")
    print("  Abre tu navegador en: http://localhost:8501")
    print()
    print("  (Presiona Ctrl+C para detener todo)")
    print("=" * 58 + "\n")

    # Arrancar Streamlit — bloquea hasta Ctrl+C
    try:
        subprocess.run(
            [
                sys.executable, "-m", "streamlit", "run", "frontend/app.py",
                "--server.port=8501",
                "--server.headless=true",
                "--server.address=localhost",
            ],
            env={**os.environ, "BACKEND_URL": "http://localhost:5000"},
        )
    except KeyboardInterrupt:
        print("\n\n👋 Demo detenida. ¡Hasta pronto!")
