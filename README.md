# 🏥 PROYECTO SALUD DIGITAL

Sistema de gestión clínica basado en estándares **FHIR R4**, con API REST en Flask,
base de datos PostgreSQL y dashboard interactivo en Streamlit.

---

## 📋 Tabla de Contenidos

- [Estructura del Proyecto](#estructura-del-proyecto)
- [Requisitos Previos](#requisitos-previos)
- [Instalación Rápida](#instalación-rápida)
- [Configuración](#configuración)
- [Ejecutar el Proyecto](#ejecutar-el-proyecto)
- [API Endpoints](#api-endpoints)
- [Autenticación Double API Key](#autenticación-double-api-key)
- [Encriptación de Datos Sensibles](#encriptación-de-datos-sensibles)
- [Paginación](#paginación)
- [Docker (opcional)](#docker-opcional)

---

## 📁 Estructura del Proyecto

```
PROYECTO-SALUD-DIGITAL/
├── backend/
│   ├── app.py              ← API principal Flask
│   ├── models.py           ← Modelos SQLAlchemy (Patient, Observation, User)
│   ├── config.py           ← Configuración desde variables de entorno
│   ├── routes/
│   │   ├── auth.py         ← Endpoints de autenticación
│   │   ├── patients.py     ← CRUD de pacientes
│   │   └── observations.py ← CRUD de observaciones
│   └── utils/
│       ├── security.py     ← Decorador Double API Key + rate limiting
│       ├── encryption.py   ← Encriptación Fernet (AES-128)
│       └── validators.py   ← Validaciones FHIR
├── frontend/
│   ├── app.py              ← App principal Streamlit
│   ├── pages/
│   │   ├── login.py        ← Página de login
│   │   ├── dashboard.py    ← Dashboard con gráficas
│   │   └── patients.py     ← Gestión de pacientes
│   └── utils/
│       └── api_client.py   ← Cliente HTTP para el backend
├── database/
│   └── init.sql            ← Script de inicialización PostgreSQL
├── requirements.txt        ← Dependencias Python
├── .env.example            ← Plantilla de variables de entorno
├── docker-compose.yml      ← Configuración Docker para desarrollo
├── Dockerfile.backend      ← Imagen Docker del backend
├── Dockerfile.frontend     ← Imagen Docker del frontend
└── README.md
```

---

## ⚙️ Requisitos Previos

- **Python 3.11+**
- **PostgreSQL 14+** (local o en la nube)
- Git

---

## 🚀 Instalación Rápida

### 1. Clonar el repositorio

```bash
git clone https://github.com/JPercy19/PROYECTO-SALUD-DIGITAL.git
cd PROYECTO-SALUD-DIGITAL
```

### 2. Crear entorno virtual e instalar dependencias

```bash
python -m venv venv
source venv/bin/activate   # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

```bash
cp .env.example .env
```

Edita el archivo `.env` con tus valores reales (ver sección [Configuración](#configuración)).

### 4. Crear la base de datos PostgreSQL

```bash
# Crear la base de datos
createdb salud_digital

# Ejecutar el script de inicialización
psql -U postgres -d salud_digital -f database/init.sql
```

### 5. Generar la clave de encriptación

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Copia la clave generada y pégala en `ENCRYPTION_KEY` de tu archivo `.env`.

---

## 🔧 Configuración

Edita el archivo `.env` con los siguientes valores:

| Variable              | Descripción                                           | Ejemplo                          |
|-----------------------|-------------------------------------------------------|----------------------------------|
| `DATABASE_URL`        | URL de conexión a PostgreSQL                         | `postgresql://user:pass@localhost:5432/salud_digital` |
| `ENCRYPTION_KEY`      | Clave Fernet para encriptar datos sensibles          | Generada con el comando anterior |
| `ADMIN_ACCESS_KEY`    | API Key de acceso del administrador                  | Cadena aleatoria larga           |
| `ADMIN_PERMISSION_KEY`| API Key de permiso del administrador                 | Cadena aleatoria larga           |
| `FLASK_SECRET_KEY`    | Clave secreta de Flask para sesiones                 | Cadena aleatoria larga           |
| `BACKEND_URL`         | URL del backend (usada por Streamlit)                | `http://localhost:5000`          |

---

## ▶️ Ejecutar el Proyecto

### Backend (API Flask)

```bash
# Activar entorno virtual
source venv/bin/activate

# Iniciar el servidor (escucha en http://localhost:5000)
python backend/app.py
```

### Frontend (Streamlit)

En otra terminal:

```bash
source venv/bin/activate
streamlit run frontend/app.py
```

El dashboard estará disponible en **http://localhost:8501**

---

## 🔌 API Endpoints

### Health Check

| Método | Endpoint | Descripción        |
|--------|----------|--------------------|
| GET    | `/`      | Estado del servidor |

### Autenticación

| Método | Endpoint       | Descripción                       |
|--------|----------------|-----------------------------------|
| POST   | `/auth/verify` | Verificar API keys                |
| POST   | `/auth/users`  | Crear nuevo usuario (requiere auth) |

### Pacientes 👥

| Método | Endpoint                   | Descripción                  |
|--------|----------------------------|------------------------------|
| GET    | `/patients`                | Listar pacientes (paginado)  |
| POST   | `/patients`                | Crear nuevo paciente         |
| GET    | `/patients/<id>`           | Obtener paciente por ID      |
| PUT    | `/patients/<id>`           | Actualizar paciente          |
| DELETE | `/patients/<id>`           | Eliminar paciente            |
| GET    | `/patients/<id>/fhir`      | Paciente en formato FHIR R4  |

### Observaciones 🔬

| Método | Endpoint                            | Descripción                         |
|--------|-------------------------------------|-------------------------------------|
| GET    | `/observations`                     | Listar observaciones (paginado)     |
| POST   | `/observations`                     | Crear observación                   |
| GET    | `/observations/<id>`                | Obtener observación por ID          |
| DELETE | `/observations/<id>`                | Eliminar observación                |
| GET    | `/observations/<id>/fhir`           | Observación en formato FHIR R4      |
| GET    | `/patients/<id>/observations`       | Observaciones de un paciente        |

---

## 🔐 Autenticación Double API Key

Todos los endpoints (excepto `/` y `/auth/verify`) requieren **dos cabeceras HTTP**:

```http
X-Access-Key:     tu-access-key
X-Permission-Key: tu-permission-key
```

**Ejemplo con curl:**

```bash
curl -H "X-Access-Key: mi-access-key" \
     -H "X-Permission-Key: mi-permission-key" \
     http://localhost:5000/patients
```

**Ejemplo con Python:**

```python
import requests

headers = {
    "X-Access-Key":     "mi-access-key",
    "X-Permission-Key": "mi-permission-key",
}
resp = requests.get("http://localhost:5000/patients", headers=headers)
print(resp.json())
```

---

## 🔒 Encriptación de Datos Sensibles

Los campos `identification_doc` (documento de identidad) y `medical_summary` (resumen médico)
se almacenan **encriptados** en la base de datos usando el algoritmo **Fernet**, que combina:

- **AES-128 en modo CBC** para cifrar los datos.
- **HMAC-SHA256** para autenticar el mensaje (integridad garantizada).

- La clave de encriptación se gestiona con la variable `ENCRYPTION_KEY`.
- Los datos se desencriptan automáticamente al leerlos por la API.
- Si se pierde la clave, los datos encriptados **no se pueden recuperar**.

---

## 📄 Paginación

Los endpoints de listado admiten los parámetros:

| Parámetro | Tipo | Por defecto | Máximo | Descripción         |
|-----------|------|-------------|--------|---------------------|
| `limit`   | int  | 20          | 100    | Resultados por página |
| `offset`  | int  | 0           | -      | Desde qué registro  |

**Ejemplo:**

```bash
# Página 2 con 10 resultados
GET /patients?limit=10&offset=10
```

**Respuesta:**

```json
{
  "data": [...],
  "total": 42,
  "limit": 10,
  "offset": 10
}
```

---

## 🐳 Docker (opcional)

Para ejecutar todo con Docker sin instalar nada localmente:

```bash
# 1. Copiar y editar variables de entorno
cp .env.example .env
# Edita .env con tus valores

# 2. Iniciar todos los servicios
docker-compose up -d

# 3. Ver el estado
docker-compose ps

# 4. Ver logs del backend
docker-compose logs backend
```

Servicios disponibles:
- **API Backend:** http://localhost:5000
- **Frontend Streamlit:** http://localhost:8501
- **PostgreSQL:** localhost:5432

---

## 🛡️ Seguridad

- **Double API Key:** Doble capa de autenticación en cada petición.
- **Rate Limiting:** Máximo 100 peticiones/minuto por IP (configurable).
- **Encriptación:** Campos sensibles cifrados con Fernet.
- **Variables de entorno:** Credenciales nunca en el código fuente.

---

## 📚 Tecnologías Utilizadas

| Componente  | Tecnología        |
|-------------|-------------------|
| Backend API | Flask 3.x         |
| ORM         | SQLAlchemy 2.x    |
| Base de datos | PostgreSQL 16   |
| Encriptación | cryptography (Fernet) |
| Rate Limiting | Flask-Limiter  |
| Frontend    | Streamlit 1.x     |
| Gráficas    | Plotly            |
| Datos FHIR  | FHIR R4 (JSON)    |

