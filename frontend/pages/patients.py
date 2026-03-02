"""
frontend/pages/patients.py - Gestión de pacientes

Permite:
  - Listar pacientes con paginación y búsqueda
  - Ver detalle de un paciente y sus observaciones
  - Crear nuevo paciente
  - Editar paciente existente
  - Eliminar paciente
"""

import streamlit as st
import pandas as pd
import requests
from frontend.utils.api_client import APIClient


def show_patients(client: APIClient):
    """
    Renderiza la página de gestión de pacientes.

    Args:
        client: Instancia autenticada de APIClient.
    """
    st.title("👥 Gestión de Pacientes")
    st.markdown("---")

    # ------------------------------------------------------------------
    # Pestañas: Listado | Nuevo Paciente
    # ------------------------------------------------------------------
    tab_list, tab_new = st.tabs(["📋 Listado", "➕ Nuevo Paciente"])

    # ==================== PESTAÑA: LISTADO ====================
    with tab_list:
        _show_patient_list(client)

    # ==================== PESTAÑA: NUEVO PACIENTE ====================
    with tab_new:
        _show_create_patient_form(client)


def _show_patient_list(client: APIClient):
    """Muestra la tabla de pacientes con búsqueda y paginación."""
    # Barra de búsqueda
    col_search, col_limit = st.columns([3, 1])
    with col_search:
        name_filter = st.text_input("🔍 Buscar por nombre", placeholder="Ej: Juan")
    with col_limit:
        limit = st.selectbox("Resultados por página", [10, 20, 50], index=1)

    # Paginación
    if "patient_offset" not in st.session_state:
        st.session_state["patient_offset"] = 0
    offset = st.session_state["patient_offset"]

    # Cargar datos
    try:
        result = client.get_patients(limit=limit, offset=offset, name=name_filter)
    except Exception as e:
        st.error(f"❌ Error al cargar pacientes: {e}")
        return

    patients = result.get("data", [])
    total    = result.get("total", 0)

    st.markdown(f"**Total:** {total} pacientes encontrados")

    if not patients:
        st.info("No hay pacientes que coincidan con la búsqueda.")
        return

    # Tabla de pacientes
    df = pd.DataFrame(patients)[["id", "name", "birth_date", "gender", "phone", "email"]]
    df.columns = ["ID", "Nombre", "F. Nacimiento", "Género", "Teléfono", "Email"]
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Controles de paginación
    col_prev, col_info, col_next = st.columns([1, 2, 1])
    with col_prev:
        if st.button("⬅️ Anterior", disabled=(offset == 0)):
            st.session_state["patient_offset"] = max(0, offset - limit)
            st.rerun()
    with col_info:
        st.markdown(
            f"<div style='text-align:center'>Página {offset // limit + 1} "
            f"de {max(1, -(-total // limit))}</div>",
            unsafe_allow_html=True,
        )
    with col_next:
        if st.button("Siguiente ➡️", disabled=(offset + limit >= total)):
            st.session_state["patient_offset"] = offset + limit
            st.rerun()

    st.markdown("---")

    # ------------------------------------------------------------------
    # Panel de detalle / acciones
    # ------------------------------------------------------------------
    st.subheader("🔍 Ver / Editar / Eliminar paciente")
    patient_id = st.number_input("ID del paciente", min_value=1, step=1, value=1)

    col_view, col_edit, col_delete = st.columns(3)

    with col_view:
        if st.button("👁️ Ver detalle", use_container_width=True):
            _show_patient_detail(client, patient_id)

    with col_edit:
        if st.button("✏️ Editar", use_container_width=True):
            st.session_state["editing_patient_id"] = patient_id

    with col_delete:
        if st.button("🗑️ Eliminar", use_container_width=True):
            if st.session_state.get("confirm_delete") == patient_id:
                try:
                    client.delete_patient(patient_id)
                    st.success(f"✅ Paciente {patient_id} eliminado.")
                    st.session_state.pop("confirm_delete", None)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error al eliminar: {e}")
            else:
                st.session_state["confirm_delete"] = patient_id
                st.warning(f"⚠️ ¿Confirmar eliminación del paciente {patient_id}? Pulsa de nuevo para confirmar.")

    # Formulario de edición (si se está editando)
    if st.session_state.get("editing_patient_id") == patient_id:
        _show_edit_patient_form(client, patient_id)


def _show_patient_detail(client: APIClient, patient_id: int):
    """Muestra el detalle completo de un paciente."""
    try:
        patient = client.get_patient(patient_id)
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ Paciente {patient_id} no encontrado." if e.response.status_code == 404 else str(e))
        return
    except Exception as e:
        st.error(f"❌ Error: {e}")
        return

    with st.expander(f"📋 Detalle del Paciente #{patient_id}", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Nombre:** {patient.get('name')}")
            st.write(f"**FHIR ID:** {patient.get('fhir_id')}")
            st.write(f"**Género:** {patient.get('gender', 'N/A')}")
            st.write(f"**F. Nacimiento:** {patient.get('birth_date', 'N/A')}")
        with col2:
            st.write(f"**Teléfono:** {patient.get('phone', 'N/A')}")
            st.write(f"**Email:** {patient.get('email', 'N/A')}")
            st.write(f"**Doc. Identificación:** {patient.get('identification_doc', '***')}")
            st.write(f"**Resumen médico:** {patient.get('medical_summary', '***')}")

    # Observaciones del paciente
    try:
        obs_result = client.get_patient_observations(patient_id)
        observations = obs_result.get("data", [])
        if observations:
            st.subheader(f"🔬 Observaciones del paciente ({obs_result.get('total', 0)} total)")
            df_obs = pd.DataFrame(observations)[[
                "id", "code", "display", "value", "unit", "status", "is_outlier", "effective_date"
            ]]
            df_obs.columns = ["ID", "Código", "Descripción", "Valor", "Unidad", "Estado", "Outlier", "Fecha"]
            st.dataframe(df_obs, use_container_width=True, hide_index=True)
        else:
            st.info("Este paciente no tiene observaciones registradas.")
    except Exception:
        pass


def _show_create_patient_form(client: APIClient):
    """Formulario para crear un nuevo paciente."""
    st.subheader("➕ Registrar nuevo paciente")

    with st.form("create_patient_form"):
        name               = st.text_input("Nombre completo *", placeholder="Ej: María García López")
        col1, col2 = st.columns(2)
        with col1:
            birth_date = st.date_input("Fecha de nacimiento", value=None)
        with col2:
            gender = st.selectbox("Género", ["", "male", "female", "other", "unknown"])

        identification_doc = st.text_input(
            "Documento de identificación",
            placeholder="Ej: 12345678A",
            help="Se almacena encriptado",
        )
        medical_summary = st.text_area(
            "Resumen médico",
            placeholder="Ej: Hipertensión arterial, Diabetes tipo 2",
            help="Se almacena encriptado",
        )
        col3, col4 = st.columns(2)
        with col3:
            phone = st.text_input("Teléfono", placeholder="+34 600 000 000")
        with col4:
            email = st.text_input("Email", placeholder="paciente@ejemplo.com")

        submitted = st.form_submit_button("💾 Guardar paciente", use_container_width=True)

    if submitted:
        if not name.strip():
            st.error("⚠️ El nombre es obligatorio.")
            return

        payload = {
            "name":   name.strip(),
            "gender": gender if gender else None,
        }
        if birth_date:
            payload["birth_date"] = birth_date.isoformat()
        if identification_doc:
            payload["identification_doc"] = identification_doc
        if medical_summary:
            payload["medical_summary"] = medical_summary
        if phone:
            payload["phone"] = phone
        if email:
            payload["email"] = email

        try:
            result = client.create_patient(payload)
            st.success(f"✅ Paciente creado con ID: {result['patient']['id']}")
        except requests.exceptions.HTTPError as e:
            try:
                detail = e.response.json()
            except Exception:
                detail = str(e)
            st.error(f"❌ Error al crear paciente: {detail}")
        except Exception as e:
            st.error(f"❌ Error de conexión: {e}")


def _show_edit_patient_form(client: APIClient, patient_id: int):
    """Formulario inline para editar un paciente existente."""
    try:
        patient = client.get_patient(patient_id)
    except Exception as e:
        st.error(f"❌ Error al cargar paciente: {e}")
        return

    st.markdown("---")
    st.subheader(f"✏️ Editando paciente #{patient_id}")

    with st.form(f"edit_patient_{patient_id}"):
        name   = st.text_input("Nombre completo *", value=patient.get("name", ""))
        gender_options = ["", "male", "female", "other", "unknown"]
        current_gender = patient.get("gender", "") or ""
        gender_index   = gender_options.index(current_gender) if current_gender in gender_options else 0
        gender = st.selectbox("Género", gender_options, index=gender_index)
        phone = st.text_input("Teléfono", value=patient.get("phone") or "")
        email = st.text_input("Email",    value=patient.get("email") or "")

        col_save, col_cancel = st.columns(2)
        with col_save:
            saved = st.form_submit_button("💾 Guardar cambios", use_container_width=True)
        with col_cancel:
            cancelled = st.form_submit_button("❌ Cancelar", use_container_width=True)

    if saved:
        payload = {"name": name.strip()}
        if gender:
            payload["gender"] = gender
        if phone:
            payload["phone"] = phone
        if email:
            payload["email"] = email

        try:
            client.update_patient(patient_id, payload)
            st.success("✅ Paciente actualizado correctamente.")
            st.session_state.pop("editing_patient_id", None)
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error al actualizar: {e}")

    if cancelled:
        st.session_state.pop("editing_patient_id", None)
        st.rerun()
