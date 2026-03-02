"""
frontend/app.py - Aplicación principal Streamlit

Punto de entrada del frontend. Gestiona:
  - Sesión de usuario (autenticación)
  - Navegación entre páginas
  - Renderizado de la interfaz principal

Ejecutar con:
    streamlit run frontend/app.py
"""

import streamlit as st

# ──────────────────────────────────────────────────────────────
# Configuración global de la página (debe ser la primera llamada)
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Salud Digital",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Importaciones después de set_page_config
from frontend.pages.login import show_login
from frontend.pages.dashboard import show_dashboard
from frontend.pages.patients import show_patients
from frontend.utils.api_client import APIClient


def main():
    """Punto de entrada principal de la aplicación."""

    # ------------------------------------------------------------------
    # Verificar autenticación
    # ------------------------------------------------------------------
    if not st.session_state.get("authenticated", False):
        show_login()
        return

    # ------------------------------------------------------------------
    # Usuario autenticado: crear cliente API
    # ------------------------------------------------------------------
    client = APIClient(
        access_key=st.session_state["access_key"],
        permission_key=st.session_state["permission_key"],
    )

    # ------------------------------------------------------------------
    # Barra lateral de navegación
    # ------------------------------------------------------------------
    with st.sidebar:
        st.image(
            "https://www.hl7.org/fhir/assets/images/fhir-logo-www.png",
            width=120,
        )
        st.title("🏥 Salud Digital")
        st.markdown("---")

        page = st.radio(
            "Navegación",
            options=["📊 Dashboard", "👥 Pacientes"],
            label_visibility="collapsed",
        )

        st.markdown("---")
        st.markdown(f"**Usuario:** {st.session_state.get('access_key', '')[:8]}...")

        if st.button("🚪 Cerrar sesión", use_container_width=True):
            for key in ["authenticated", "access_key", "permission_key"]:
                st.session_state.pop(key, None)
            st.rerun()

    # ------------------------------------------------------------------
    # Renderizar la página seleccionada
    # ------------------------------------------------------------------
    if page == "📊 Dashboard":
        show_dashboard(client)
    elif page == "👥 Pacientes":
        show_patients(client)


if __name__ == "__main__":
    main()
