# 🏥 CÓMO EMPEZAR — Guía Completa de Instalación

> Esta guía te explica **paso a paso** todo lo que necesitas instalar y configurar
> para que el proyecto **Salud Digital** funcione en tu computadora.
>
> Hay **tres caminos** según lo que prefieras:
> - 🟢 **Camino A — Demo rápida** (5 minutos, sin PostgreSQL, recomendado para ver la app)
> - 🔵 **Camino B — Instalación local completa** (con PostgreSQL real)
> - 🟣 **Camino C — Con Docker** (el más limpio, requiere Docker instalado)

---

## 📋 Índice

1. [Requisitos previos — qué instalar primero](#1-requisitos-previos--qué-instalar-primero)
2. [Descargar el proyecto](#2-descargar-el-proyecto)
3. [🟢 Camino A — Demo rápida (recomendado)](#3-camino-a--demo-rápida-recomendado)
4. [🔵 Camino B — Instalación completa con PostgreSQL](#4-camino-b--instalación-completa-con-postgresql)
5. [🟣 Camino C — Con Docker (opcional)](#5-camino-c--con-docker-opcional)
6. [Cómo usar la aplicación](#6-cómo-usar-la-aplicación)
7. [Solución de problemas frecuentes](#7-solución-de-problemas-frecuentes)

---

## 1. Requisitos previos — qué instalar primero

### ✅ Para cualquier camino

| Programa | Versión mínima | Dónde descargarlo |
|----------|---------------|-------------------|
| **Python** | 3.10 o superior | https://www.python.org/downloads/ |
| **Git** | Cualquiera | https://git-scm.com/downloads |

#### Cómo verificar que ya los tienes instalados

Abre una terminal (CMD, PowerShell o la terminal de tu sistema) y escribe:

```bash
python --version
# Debe mostrar algo como: Python 3.12.x

git --version
# Debe mostrar algo como: git version 2.x.x
```

> **Windows:** si `python` no funciona, prueba con `python3` o `py`.
> Si ninguno funciona, asegúrate de marcar **"Add Python to PATH"** durante la instalación.

---

### 🔵 Solo para el Camino B (PostgreSQL local)

| Programa | Versión mínima | Dónde descargarlo |
|----------|---------------|-------------------|
| **PostgreSQL** | 14 o superior | https://www.postgresql.org/download/ |

Durante la instalación de PostgreSQL se te pedirá una **contraseña para el usuario `postgres`**.
Anota esa contraseña, la vas a necesitar más adelante.

---

### 🟣 Solo para el Camino C (Docker)

| Programa | Dónde descargarlo |
|----------|-------------------|
| **Docker Desktop** | https://www.docker.com/products/docker-desktop/ |

---

## 2. Descargar el proyecto

Si todavía no tienes el proyecto en tu computadora:

```bash
git clone https://github.com/JPercy19/PROYECTO-SALUD-DIGITAL.git
cd PROYECTO-SALUD-DIGITAL
```

Si ya lo tienes, solo asegúrate de estar dentro de la carpeta del proyecto:

```bash
cd PROYECTO-SALUD-DIGITAL
```

---

## 3. 🟢 Camino A — Demo rápida (recomendado)

> ✅ **No necesitas PostgreSQL ni configurar nada.**
> El script crea su propia base de datos local y arranca todo automáticamente.

### Paso 1 — Instalar las dependencias de Python

```bash
pip install -r requirements.txt
```

> Esto descarga e instala todas las librerías que necesita el proyecto.
> Solo tienes que hacerlo **una vez**.

### Paso 2 — Ejecutar la demo

```bash
python demo.py
```

El script hace todo solo:

- Crea una base de datos SQLite en tu carpeta (`demo_salud_digital.db`)
- Carga 4 pacientes con datos clínicos de ejemplo
- Arranca el backend en `http://localhost:5000`
- Arranca el frontend en **`http://localhost:8501`**
- Muestra las credenciales en pantalla

### Paso 3 — Abrir la aplicación

Abre tu navegador y ve a: **http://localhost:8501**

Inicia sesión con:

```
X-Access-Key:     demo-access-key
X-Permission-Key: demo-permission-key
```

### Para detener todo

Pulsa **Ctrl + C** en la terminal.

---

## 4. 🔵 Camino B — Instalación completa con PostgreSQL

Sigue este camino si quieres usar la base de datos real (PostgreSQL).

### Paso 1 — Instalar las dependencias de Python

```bash
pip install -r requirements.txt
```

### Paso 2 — Crear la base de datos en PostgreSQL

Abre la herramienta de PostgreSQL. Puedes usar **pgAdmin** (interfaz gráfica)
o la línea de comandos `psql`.

**Con psql:**

```bash
psql -U postgres
```

Dentro de psql, ejecuta:

```sql
CREATE DATABASE salud_digital;
\q
```

Luego aplica el script de inicialización:

```bash
psql -U postgres -d salud_digital -f database/init.sql
```

### Paso 3 — Generar las claves del proyecto

Necesitas tres claves:

#### a) Clave de encriptación (ENCRYPTION_KEY)

Ejecuta este comando en la terminal:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Copia el resultado. Se verá así (el tuyo será diferente):
```
XfJ8kLmN2pQrSt3uVwXyZ4AbCdEfGhIjKlMnOpQrSt=
```

#### b) API Keys de administrador

Puedes inventarlas tú mismo. Usa cadenas largas y difíciles de adivinar.
Ejemplo sencillo para desarrollo:

```
ADMIN_ACCESS_KEY:     mi-clave-acceso-2024
ADMIN_PERMISSION_KEY: mi-clave-permiso-2024
```

#### c) Clave secreta de Flask

Invéntala también:

```
FLASK_SECRET_KEY: mi-clave-flask-super-secreta
```

### Paso 4 — Crear el archivo `.env`

En la raíz del proyecto hay un archivo llamado `.env.example`.
Cópialo y renómbralo como `.env`:

**En Windows (CMD):**
```cmd
copy .env.example .env
```

**En Mac/Linux:**
```bash
cp .env.example .env
```

Abre el archivo `.env` con cualquier editor de texto (Notepad, VS Code, etc.)
y rellena los valores con los que generaste en el paso anterior:

```env
# Cambia "usuario" y "contraseña" por los de tu PostgreSQL
DATABASE_URL=postgresql://postgres:TU_CONTRASEÑA_POSTGRES@localhost:5432/salud_digital

# La clave que generaste con Fernet
ENCRYPTION_KEY=XfJ8kLmN2pQrSt3uVwXyZ4AbCdEfGhIjKlMnOpQrSt=

# Tus API keys de administrador
ADMIN_ACCESS_KEY=mi-clave-acceso-2024
ADMIN_PERMISSION_KEY=mi-clave-permiso-2024

# Claves de Flask
FLASK_ENV=development
FLASK_SECRET_KEY=mi-clave-flask-super-secreta

# Deja estas dos igual
RATELIMIT_STORAGE_URL=memory://
BACKEND_URL=http://localhost:5000
```

### Paso 5 — Arrancar el backend (Flask)

Abre una terminal y ejecuta:

```bash
python backend/app.py
```

Debes ver algo así:
```
🚀 Salud Digital API escuchando en http://localhost:5000
```

**Deja esta terminal abierta.**

### Paso 6 — Arrancar el frontend (Streamlit)

Abre **otra terminal** (sin cerrar la anterior) y ejecuta:

```bash
streamlit run frontend/app.py
```

El frontend se abrirá automáticamente en tu navegador en: **http://localhost:8501**

### Paso 7 — Iniciar sesión

Usa las API keys que pusiste en tu `.env`:

```
X-Access-Key:     mi-clave-acceso-2024
X-Permission-Key: mi-clave-permiso-2024
```

---

## 5. 🟣 Camino C — Con Docker (opcional)

> Usa este camino si tienes Docker instalado y quieres la solución más limpia:
> no necesitas instalar Python, PostgreSQL ni configurar nada en tu sistema.

### Paso 1 — Crear el archivo `.env`

Igual que en el Camino B, copia `.env.example` como `.env` y rellena las claves.
Como mínimo necesitas poner la `ENCRYPTION_KEY` (generarla como se explicó arriba).

### Paso 2 — Arrancar todo con un solo comando

```bash
docker-compose up -d
```

Docker descargará las imágenes necesarias, creará los contenedores y arrancará
la base de datos, el backend y el frontend automáticamente.

La primera vez puede tardar varios minutos mientras descarga todo.

### Paso 3 — Abrir la aplicación

- **Frontend:** http://localhost:8501
- **Backend (API):** http://localhost:5000

### Para detener los contenedores

```bash
docker-compose down
```

### Para ver los logs si algo falla

```bash
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db
```

---

## 6. Cómo usar la aplicación

Una vez que hayas iniciado sesión con tus credenciales, encontrarás:

### Dashboard principal
- Gráficas con la evolución de las observaciones clínicas
- Resumen estadístico de pacientes
- Alertas de valores fuera de rango (outliers)

### Gestión de pacientes
- Ver listado de pacientes
- Crear nuevos pacientes
- Ver detalle de cada paciente con sus observaciones clínicas

### API REST (para desarrolladores)
El backend expone una API documentada. Endpoints principales:

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/` | Estado del servicio |
| POST | `/auth/verify` | Verificar credenciales |
| GET | `/patients` | Listar pacientes |
| POST | `/patients` | Crear paciente |
| GET | `/patients/{id}` | Ver paciente |
| GET | `/observations` | Listar observaciones |
| POST | `/observations` | Crear observación |

Todas las rutas (excepto `/`) requieren las cabeceras:
```
X-Access-Key: tu-clave-acceso
X-Permission-Key: tu-clave-permiso
```

---

## 7. Solución de problemas frecuentes

### ❌ "python no se reconoce como comando"
- **Windows:** durante la instalación de Python, marca la casilla **"Add Python to PATH"**
- O usa `py` en lugar de `python`

### ❌ "No module named 'flask'" u otro módulo
Significa que las dependencias no están instaladas. Ejecuta:
```bash
pip install -r requirements.txt
```

### ❌ El backend dice "could not connect to server" (PostgreSQL)
- Verifica que PostgreSQL está corriendo en tu sistema
- Verifica que la contraseña en `DATABASE_URL` del `.env` es correcta
- Verifica que la base de datos `salud_digital` existe:
  ```bash
  psql -U postgres -l
  ```

### ❌ El frontend muestra "backend no disponible"
- Asegúrate de que el backend (Flask) está corriendo en otra terminal
- Verifica que `BACKEND_URL=http://localhost:5000` está en tu `.env`

### ❌ Error de ENCRYPTION_KEY
La clave debe tener exactamente el formato Fernet (44 caracteres en Base64).
Genérala así:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### ❌ "Port 5000 already in use"
Otro programa está usando el puerto 5000. Puedes cambiar el puerto:
```bash
BACKEND_PORT=5001 python backend/app.py
```
Y actualiza `BACKEND_URL=http://localhost:5001` en tu `.env`.

### ❌ "Port 8501 already in use"
```bash
streamlit run frontend/app.py --server.port 8502
```

---

## 📌 Resumen de archivos importantes

| Archivo | Para qué sirve |
|---------|---------------|
| `demo.py` | Arrancar la demo completa sin configurar nada |
| `.env` | Variables de configuración (debes crearlo tú a partir de `.env.example`) |
| `.env.example` | Plantilla del `.env` con explicaciones |
| `requirements.txt` | Lista de librerías Python a instalar |
| `database/init.sql` | Script para inicializar la base de datos PostgreSQL |
| `backend/app.py` | Servidor API (Flask) |
| `frontend/app.py` | Dashboard web (Streamlit) |
| `docker-compose.yml` | Configuración para arrancar todo con Docker |

---

> **¿Primera vez con el proyecto?** Empieza por el **Camino A** (`python demo.py`).
> Es la forma más rápida de ver la aplicación funcionando sin tener que configurar nada.
