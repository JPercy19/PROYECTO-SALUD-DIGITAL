"""
frontend/pages/login.py - Página de inicio de sesión

Muestra un formulario para ingresar las API keys Double Key.
Si la autenticación es exitosa, guarda las credenciales en la
sesión de Streamlit (st.session_state).
"""

import streamlit as st
from frontend.utils.api_client import APIClient


def show_login():
    """
    Renderiza la página de login y gestiona la autenticación.
    Retorna True si el usuario se autenticó correctamente.
    """
    st.title("🏥 Salud Digital - Acceso al Sistema")
    st.markdown("---")

    st.markdown("""
    ### Bienvenido al Sistema de Gestión Clínica

    Este sistema utiliza **Double API Key** para mayor seguridad:
    - **X-Access-Key**: Identifica tu cuenta de usuario.
    - **X-Permission-Key**: Autoriza el acceso a los datos clínicos.
    """)

    with st.form("login_form"):
        st.subheader("🔑 Ingresar credenciales")

        access_key = st.text_input(
            "X-Access-Key",
            type="password",
            placeholder="Ingresa tu clave de acceso",
            help="Proporcionada por el administrador del sistema",
        )
        permission_key = st.text_input(
            "X-Permission-Key",
            type="password",
            placeholder="Ingresa tu clave de permiso",
            help="Segunda clave de seguridad",
        )

        submitted = st.form_submit_button("🚀 Iniciar sesión", use_container_width=True)

    if submitted:
        if not access_key or not permission_key:
            st.error("⚠️ Debes ingresar ambas claves para continuar.")
            return False

        with st.spinner("Verificando credenciales..."):
            is_valid = APIClient.verify_keys(access_key, permission_key)

        if is_valid:
            st.session_state["authenticated"]  = True
            st.session_state["access_key"]     = access_key
            st.session_state["permission_key"] = permission_key
            st.success("✅ Autenticación exitosa. Redirigiendo...")
            st.rerun()
            return True
        else:
            st.error("❌ Credenciales incorrectas o el backend no está disponible.")
            return False

    return False
