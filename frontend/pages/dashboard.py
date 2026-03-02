"""
frontend/pages/dashboard.py - Dashboard principal de gestión clínica

Muestra:
  - Métricas generales (total pacientes, observaciones, outliers)
  - Gráfica de tendencias de observaciones por tipo
  - Tabla de observaciones con alertas de outliers
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from frontend.utils.api_client import APIClient


def show_dashboard(client: APIClient):
    """
    Renderiza el dashboard principal.

    Args:
        client: Instancia autenticada de APIClient.
    """
    st.title("📊 Dashboard Clínico")
    st.markdown("---")

    # ------------------------------------------------------------------
    # Cargar datos
    # ------------------------------------------------------------------
    try:
        patients_data     = client.get_patients(limit=100)
        observations_data = client.get_observations(limit=500)
    except Exception as e:
        st.error(f"❌ Error al conectar con la API: {e}")
        st.info("Asegúrate de que el backend está en ejecución.")
        return

    patients     = patients_data.get("data", [])
    observations = observations_data.get("data", [])

    # ------------------------------------------------------------------
    # Métricas generales (KPIs)
    # ------------------------------------------------------------------
    total_patients     = patients_data.get("total", len(patients))
    total_observations = observations_data.get("total", len(observations))
    outliers           = [o for o in observations if o.get("is_outlier")]

    col1, col2, col3 = st.columns(3)
    col1.metric("👥 Total Pacientes",     total_patients)
    col2.metric("🔬 Total Observaciones", total_observations)
    col3.metric(
        "⚠️ Outliers",
        len(outliers),
        delta=f"{len(outliers)} alertas",
        delta_color="inverse",
    )

    st.markdown("---")

    # ------------------------------------------------------------------
    # Gráfica de tendencias por tipo de observación
    # ------------------------------------------------------------------
    if observations:
        df = pd.DataFrame(observations)

        # Convertir fecha a datetime
        if "effective_date" in df.columns:
            df["effective_date"] = pd.to_datetime(df["effective_date"], errors="coerce")

        st.subheader("📈 Tendencias de Observaciones")

        # Selector de tipo de observación
        codes = df["code"].dropna().unique().tolist() if "code" in df.columns else []
        if codes:
            selected_code = st.selectbox(
                "Seleccionar tipo de observación (código LOINC):",
                options=codes,
                format_func=lambda c: (
                    df[df["code"] == c]["display"].iloc[0]
                    if not df[df["code"] == c]["display"].isna().all()
                    else c
                ),
            )

            df_filtered = df[df["code"] == selected_code].copy()

            if not df_filtered.empty and "value" in df_filtered.columns:
                # Ordenar por fecha
                df_filtered = df_filtered.sort_values("effective_date")

                fig = go.Figure()

                # Línea de valores
                fig.add_trace(go.Scatter(
                    x=df_filtered["effective_date"],
                    y=df_filtered["value"],
                    mode="lines+markers",
                    name="Valor",
                    line=dict(color="#1f77b4", width=2),
                    marker=dict(
                        color=[
                            "red" if o else "#1f77b4"
                            for o in df_filtered.get("is_outlier", [False] * len(df_filtered))
                        ],
                        size=8,
                    ),
                ))

                # Líneas de referencia (si existen)
                ref_low_val = None
                ref_high_val = None
                if "ref_low" in df_filtered.columns:
                    non_null_low = df_filtered["ref_low"].dropna()
                    if not non_null_low.empty:
                        ref_low_val = non_null_low.iloc[0]
                if "ref_high" in df_filtered.columns:
                    non_null_high = df_filtered["ref_high"].dropna()
                    if not non_null_high.empty:
                        ref_high_val = non_null_high.iloc[0]

                if ref_low_val is not None:
                    fig.add_hline(
                        y=float(ref_low_val),
                        line_dash="dash",
                        line_color="orange",
                        annotation_text="Mínimo normal",
                    )
                if ref_high_val is not None:
                    fig.add_hline(
                        y=float(ref_high_val),
                        line_dash="dash",
                        line_color="red",
                        annotation_text="Máximo normal",
                    )

                unit_col = df_filtered["unit"].dropna() if "unit" in df_filtered.columns else []
                unit_label = unit_col.iloc[0] if len(unit_col) > 0 else ""
                fig.update_layout(
                    title=f"Tendencia: {selected_code}",
                    xaxis_title="Fecha",
                    yaxis_title=unit_label,
                    hovermode="x unified",
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No hay valores numéricos para graficar.")
    else:
        st.info("ℹ️ No hay observaciones registradas todavía.")

    st.markdown("---")

    # ------------------------------------------------------------------
    # Tabla de outliers
    # ------------------------------------------------------------------
    if outliers:
        st.subheader("⚠️ Alertas de Outliers")
        df_outliers = pd.DataFrame(outliers)[
            ["patient_id", "code", "display", "value", "unit", "ref_low", "ref_high", "effective_date"]
        ]
        st.dataframe(df_outliers, use_container_width=True)
    else:
        st.success("✅ No se detectaron outliers en las observaciones recientes.")

    # ------------------------------------------------------------------
    # Distribución por género
    # ------------------------------------------------------------------
    if patients:
        st.markdown("---")
        st.subheader("👥 Distribución de Pacientes por Género")
        df_patients = pd.DataFrame(patients)
        if "gender" in df_patients.columns:
            gender_counts = df_patients["gender"].value_counts().reset_index()
            gender_counts.columns = ["Género", "Cantidad"]
            fig_gender = px.pie(
                gender_counts,
                names="Género",
                values="Cantidad",
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
            st.plotly_chart(fig_gender, use_container_width=True)
