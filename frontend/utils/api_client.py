"""
frontend/utils/api_client.py - Cliente HTTP para comunicarse con la API backend

Centraliza todas las llamadas a la API REST de Salud Digital.
Maneja automáticamente las cabeceras de autenticación.
"""

import os
import requests
from typing import Optional


# URL base del backend (configurable por variable de entorno)
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:5000")

# Timeout por defecto para las peticiones (segundos)
DEFAULT_TIMEOUT = 10


class APIClient:
    """
    Cliente para la API REST de Salud Digital.

    Uso:
        client = APIClient(access_key="...", permission_key="...")
        pacientes = client.get_patients()
    """

    def __init__(self, access_key: str, permission_key: str):
        """
        Inicializa el cliente con las credenciales Double API Key.

        Args:
            access_key:     Valor de la cabecera X-Access-Key.
            permission_key: Valor de la cabecera X-Permission-Key.
        """
        self.base_url = BACKEND_URL.rstrip("/")
        self.headers  = {
            "X-Access-Key":     access_key,
            "X-Permission-Key": permission_key,
            "Content-Type":     "application/json",
        }

    def _get(self, path: str, params: Optional[dict] = None) -> dict:
        """Realiza una petición GET y devuelve el JSON de respuesta."""
        resp = requests.get(
            f"{self.base_url}{path}",
            headers=self.headers,
            params=params,
            timeout=DEFAULT_TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json()

    def _post(self, path: str, body: dict) -> dict:
        """Realiza una petición POST con body JSON."""
        resp = requests.post(
            f"{self.base_url}{path}",
            headers=self.headers,
            json=body,
            timeout=DEFAULT_TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json()

    def _put(self, path: str, body: dict) -> dict:
        """Realiza una petición PUT con body JSON."""
        resp = requests.put(
            f"{self.base_url}{path}",
            headers=self.headers,
            json=body,
            timeout=DEFAULT_TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json()

    def _delete(self, path: str) -> dict:
        """Realiza una petición DELETE."""
        resp = requests.delete(
            f"{self.base_url}{path}",
            headers=self.headers,
            timeout=DEFAULT_TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json()

    # ------------------------------------------------------------------
    # Autenticación
    # ------------------------------------------------------------------

    @staticmethod
    def verify_keys(access_key: str, permission_key: str) -> bool:
        """
        Verifica las API keys contra el backend.

        Returns:
            True si las credenciales son válidas, False en caso contrario.
        """
        try:
            resp = requests.post(
                f"{BACKEND_URL}/auth/verify",
                headers={
                    "X-Access-Key":     access_key,
                    "X-Permission-Key": permission_key,
                },
                timeout=DEFAULT_TIMEOUT,
            )
            return resp.status_code == 200
        except requests.RequestException:
            return False

    # ------------------------------------------------------------------
    # Pacientes
    # ------------------------------------------------------------------

    def get_patients(self, limit: int = 20, offset: int = 0,
                     name: str = "") -> dict:
        """Lista pacientes con paginación y filtro opcional por nombre."""
        params = {"limit": limit, "offset": offset}
        if name:
            params["name"] = name
        return self._get("/patients", params=params)

    def get_patient(self, patient_id: int) -> dict:
        """Obtiene un paciente por su ID."""
        return self._get(f"/patients/{patient_id}")

    def create_patient(self, data: dict) -> dict:
        """Crea un nuevo paciente."""
        return self._post("/patients", data)

    def update_patient(self, patient_id: int, data: dict) -> dict:
        """Actualiza los datos de un paciente."""
        return self._put(f"/patients/{patient_id}", data)

    def delete_patient(self, patient_id: int) -> dict:
        """Elimina un paciente."""
        return self._delete(f"/patients/{patient_id}")

    # ------------------------------------------------------------------
    # Observaciones
    # ------------------------------------------------------------------

    def get_observations(self, limit: int = 20, offset: int = 0,
                         code: str = "") -> dict:
        """Lista observaciones con paginación y filtro opcional por código."""
        params = {"limit": limit, "offset": offset}
        if code:
            params["code"] = code
        return self._get("/observations", params=params)

    def get_patient_observations(self, patient_id: int, limit: int = 20,
                                 offset: int = 0) -> dict:
        """Obtiene las observaciones de un paciente."""
        return self._get(
            f"/patients/{patient_id}/observations",
            params={"limit": limit, "offset": offset},
        )

    def create_observation(self, data: dict) -> dict:
        """Crea una nueva observación clínica."""
        return self._post("/observations", data)

    def delete_observation(self, obs_id: int) -> dict:
        """Elimina una observación."""
        return self._delete(f"/observations/{obs_id}")
