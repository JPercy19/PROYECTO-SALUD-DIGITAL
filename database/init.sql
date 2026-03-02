-- ============================================================
-- PROYECTO SALUD DIGITAL - Script de inicialización PostgreSQL
-- Ejecutar: psql -U usuario -d salud_digital -f init.sql
-- ============================================================

-- Habilitar la extensión para UUIDs (opcional)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- TABLA: users
-- Almacena las credenciales de acceso a la API (Double API Key)
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id             SERIAL PRIMARY KEY,
    username       VARCHAR(100) UNIQUE NOT NULL,
    -- Las API keys se almacenan como hash SHA-256 en la app
    access_key     VARCHAR(255) NOT NULL,
    permission_key VARCHAR(255) NOT NULL,
    is_active      BOOLEAN DEFAULT TRUE,
    created_at     TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLA: patients
-- Datos del paciente en formato FHIR (recurso Patient)
-- Los campos sensibles se almacenan encriptados (Fernet)
-- ============================================================
CREATE TABLE IF NOT EXISTS patients (
    id                 SERIAL PRIMARY KEY,
    fhir_id            VARCHAR(100) UNIQUE DEFAULT uuid_generate_v4()::TEXT,
    name               VARCHAR(255) NOT NULL,
    birth_date         DATE,
    gender             VARCHAR(20) CHECK (gender IN ('male', 'female', 'other', 'unknown')),
    -- Campos sensibles encriptados
    identification_doc TEXT,   -- Número de documento encriptado
    medical_summary    TEXT,   -- Resumen médico encriptado
    -- Datos de contacto
    phone              VARCHAR(50),
    email              VARCHAR(255),
    -- Auditoría
    created_at         TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at         TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLA: observations
-- Observaciones clínicas en formato FHIR (recurso Observation)
-- ============================================================
CREATE TABLE IF NOT EXISTS observations (
    id             SERIAL PRIMARY KEY,
    patient_id     INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    fhir_id        VARCHAR(100) UNIQUE DEFAULT uuid_generate_v4()::TEXT,
    -- Código LOINC/SNOMED del tipo de observación
    code           VARCHAR(100) NOT NULL,
    display        VARCHAR(255),          -- Descripción del código
    -- Valor numérico de la observación
    value          DECIMAL(10, 4),
    unit           VARCHAR(50),           -- Unidad (ej: kg, mmHg, %)
    -- Valores de referencia para detección de outliers
    ref_low        DECIMAL(10, 4),
    ref_high       DECIMAL(10, 4),
    -- Metadatos FHIR
    status         VARCHAR(50) DEFAULT 'final'
                   CHECK (status IN ('registered', 'preliminary', 'final', 'amended', 'cancelled')),
    effective_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at     TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- ÍNDICES para mejorar el rendimiento de consultas frecuentes
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_patients_name      ON patients(name);
CREATE INDEX IF NOT EXISTS idx_patients_fhir_id   ON patients(fhir_id);
CREATE INDEX IF NOT EXISTS idx_obs_patient_id     ON observations(patient_id);
CREATE INDEX IF NOT EXISTS idx_obs_code           ON observations(code);
CREATE INDEX IF NOT EXISTS idx_obs_effective_date ON observations(effective_date);

-- ============================================================
-- TRIGGER: actualizar updated_at automáticamente en patients
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_patients_updated_at
    BEFORE UPDATE ON patients
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- DATOS INICIALES: usuario administrador de ejemplo
-- Las API keys deben cambiarse en producción
-- ============================================================
INSERT INTO users (username, access_key, permission_key)
VALUES (
    'admin',
    'admin-access-key-cambiar-en-produccion',
    'admin-permission-key-cambiar-en-produccion'
) ON CONFLICT (username) DO NOTHING;

-- Mensaje de confirmación
DO $$
BEGIN
    RAISE NOTICE 'Base de datos Salud Digital inicializada correctamente.';
END $$;
