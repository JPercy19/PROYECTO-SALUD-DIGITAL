"""
utils/encryption.py - Encriptación de datos sensibles con Fernet

Fernet es encriptación autenticada que usa:
  - AES-128 en modo CBC para cifrado
  - HMAC-SHA256 para autenticación del mensaje
Esto garantiza tanto confidencialidad como integridad de los datos.

Uso:
    from backend.utils.encryption import encrypt, decrypt

    texto_encriptado = encrypt("12345678A")
    texto_original   = decrypt(texto_encriptado)
"""

import os
from cryptography.fernet import Fernet, InvalidToken


def _get_fernet() -> Fernet:
    """
    Devuelve una instancia Fernet usando la clave del entorno.
    Lanza ValueError si la clave no está configurada.
    """
    key = os.environ.get("ENCRYPTION_KEY", "")
    if not key:
        raise ValueError(
            "La variable de entorno ENCRYPTION_KEY no está configurada. "
            "Genera una clave con: "
            "python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
        )
    return Fernet(key.encode())


def encrypt(plain_text: str) -> str:
    """
    Encripta una cadena de texto y devuelve el resultado en Base64.

    Args:
        plain_text: Texto en claro a encriptar.

    Returns:
        Cadena encriptada en formato Base64 (segura para almacenar en DB).
    """
    if not plain_text:
        return plain_text
    fernet = _get_fernet()
    return fernet.encrypt(plain_text.encode()).decode()


def decrypt(cipher_text: str) -> str:
    """
    Desencripta una cadena previamente encriptada con encrypt().

    Args:
        cipher_text: Texto encriptado en Base64.

    Returns:
        Texto original en claro. Devuelve "[error de desencriptación]"
        si el token no es válido (protección ante datos corruptos).
    """
    if not cipher_text:
        return cipher_text
    try:
        fernet = _get_fernet()
        return fernet.decrypt(cipher_text.encode()).decode()
    except InvalidToken:
        return "[error de desencriptación]"
    except ValueError as exc:
        raise exc
