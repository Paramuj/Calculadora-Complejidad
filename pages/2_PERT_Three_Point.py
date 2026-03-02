# pages/2_PERT_Three_Point.py
# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np

# ===========================
# Sidebar - Parámetros globales
# ===========================
st.sidebar.markdown("## 📊 PERT 3-Point")
unidad = st.sidebar.selectbox("Unidad de entrada", ["Días", "Horas"], index=0)
horas_por_dia = st.sidebar.number_input("Horas laborables por día", min_value=1.0, max_value=24.0, value=8.0, step=0.5)
st.sidebar.caption("Puedes capturar O, M, P en la unidad elegida; el resultado se muestra en ambas.")

# Factores de ajuste por complejidad (editables)
st.sidebar.markdown("### Ajuste por complejidad (opcional)")
default_factors = {"Eclipse": 1.00, "Galaxy": 1.05, "Quantum": 1.10, "Nova": 1.20}
factors = {}
for k, v in default_factors.items():
    factors[k] = st.sidebar.number_input(f"Factor {k}", min_value=0.8, max_value=2.0, value=float(v), step=0.01, key=f"f_{k}")

# Selección de fuente de complejidad
st.sidebar.markdown("### Fuente de complejidad")
source = st.sidebar.radio(
    "¿Cómo quieres aplicar la complejidad?",
    ["Sin ajuste", "Usar último cálculo", "Usar proyecto guardado", "Seleccionar manualmente"],
    index=0
)

complexity_label = None

if source == "Usar último cálculo":
    complexity_label = st.session_state.get("complexity_label")
    if complexity_label:
        st.sidebar.success(f"Último cálculo: **{complexity_label}**")
    else:
        st.sidebar.warning("No hay cálculo previo en esta sesión.")
        source = "Sin ajuste"

elif source == "Usar proyecto guardado":
    projects = st.session_state.get("projects", [])
    if projects:
        choice = st.sidebar.selectbox("Proyecto", [f"{p['name']} — {p['label']}" for p in projects])
        if choice:
            idx = [f"{p['name']} — {p['label']}" for p in projects].index(choice)
            complexity_label = projects[idx]["label"]
    else:
        st.sidebar.warning("No hay proyectos guardados.")
        source = "Sin ajuste"

elif source == "Seleccionar manualmente":
    complexity_label = st.sidebar.selectbox("Clasificación", ["Eclipse", "Galaxy", "Quantum", "Nova"], index=0)

# ===========================
# UI principal
# ===========================
st.title("📊 PERT — Estimación de 3 puntos")

with st.expander("¿Cómo funciona PERT? (fórmulas y ejemplo)"):
    st.markdown(
        "- **Tiempo Esperado (TE)** = (O + 4M + P) / 6  \n"
        "- **Desviación estándar (σ)** = (P − O) / 6  \n"
        "La estimación pondera el valor más probable (M) para incorporar **incertidumbre** de forma realista. "
        "Esto es útil cuando no hay datos históricos sólidos. [1](https://clockify.me/pert-analysis-chart)[2](https://clockify.me/es/diagrama-de-analisis-pert)"
    )

with st.expander("¿Por qué relacionar la complejidad con OCM (Change Management)?"):
    st.markdown(
        "La **complejidad** (tamaño del cambio, impacto cultural, liderazgo, riesgo, etc.) aumenta la probabilidad "
        "de **retrasos** y **retrabajos** por la adopción humana. La evidencia de Prosci muestra una **correlación** "
        "entre la **efectividad** de la Gestión del Cambio y el **cumplimiento de objetivos**, estar **en tiempo** y "
        "**en presupuesto**. Es decir, a mayor efectividad de CM, mejores resultados del proyecto. "
        "Por eso ofrecemos un **ajuste opcional** del TE según la complejidad para reflejar riesgos de adopción. "
        "[3](https://www.prosci.com/blog/the-correlation-between-change-management-and-project-success)[4](https://www.proscieurope.co.uk/hubfs/Best-Practices-in-Change-Management-12th-Edition-Executive-Summary.pdf?hsLang=en)"
    )

with st.expander("PERT vs CPM — ¿cuándo usar cada uno?"):
    st.markdown(
        "- **PERT** modela **incertidumbre** con tres estimaciones (O, M, P) y es ideal para proyectos **no repetitivos** "
        "o con alta variabilidad (I+D, innovación).  \n"
        "- **CPM** asume **duraciones deterministas** y prioriza la **optimización tiempo–costo**; funciona mejor con "
        "procesos **repetitivos** o con buen histórico (construcción, despliegues estandarizados).  \n"
        "En la práctica son **complementarios**: PERT para estimar duraciones realistas con variabilidad y "
        "CPM/Gantt para **secuenciar**, identificar **ruta crítica** y gestionar holguras. "
        "[5](https://www.projectmanager.com/blog/pert-and-cpm)[6](https://www.geeksforgeeks.org/software-engineering/difference-between-pert-and-cpm/)"
    )

# ===========================
# Captura de actividades
# ===========================
st.markdown("### Actividades")
num = st.number_input("Número de actividades", min_value=1, max_value=200, value=5)

def to_days(x):
    return x if unidad == "Días" else x / horas_por_dia

def to_hours(x):
    return x if unidad == "Horas" else x * horas_por_dia

rows = []
for i in range(num):
    st.subheader(f"Actividad {i+1}")
    c1, c2, c3 = st.columns(3)
    with c1:
        O = st.number_input("Optimista (O)", min_value=0.0, value=1.0, key=f"O_{i}")
    with c2:
        M = st.number_input("Más probable (M)", min_value=0.0, value=2.0, key=f"M_{i}")
    with c3:
        P = st.number_input("Pesimista (P)", min_value=0.0, value=3.0, key=f"P_{i}")

    # Convertimos todo a días para cálculo base
    O_d, M_d, P_d = to_days(O), to_days(M), to_days(P)
    TE_d = (O_d + 4*M_d + P_d) / 6.0
    sigma_d = (P_d - O_d) / 6.0

    # Ajuste por complejidad (si aplica)
    factor = 1.0
    if complexity_label in factors:
        factor = factors[complexity_label]
    TE_adj_d = TE_d * factor

    # Guardamos fila con ambas unidades
    rows.append([
        f"A{i+1}",
        O if unidad=="Días" else None, M if unidad=="Días" else None, P if unidad=="Días" else None,
        O if unidad=="Horas" else None, M if unidad=="Horas" else None, P if unidad=="Horas" else None,
        TE_d, sigma_d, TE_adj_d
    ])

# ===========================
# Resultados por actividad
# ===========================
df = pd.DataFrame(
    rows,
    columns=[
        "Actividad",
        "O (d)", "M (d)", "P (d)",
        "O (h)", "M (h)", "P (h)",
        "TE (días)", "σ (días)", "TE ajustado (días)"
    ]
)

st.markdown("### 📌 Resultados por actividad")
st.dataframe(df, use_container_width=True, hide_index=True)

# ===========================
# Totales y conversión
# ===========================
st.markdown("### 📊 Totales")

total_TE_d = df["TE (días)"].sum()
total_sigma_d = np.sqrt((df["σ (días)"]**2).sum())
total_TE_adj_d = df["TE ajustado (días)"].sum()

colA, colB, colC, colD, colE, colF = st.columns(6)
colA.metric("TE total (días)", f"{total_TE_d:.2f}")
colB.metric("σ total (días)", f"{total_sigma_d:.2f}")
colC.metric("TE ajustado (días)", f"{total_TE_adj_d:.2f}")
colD.metric("TE total (horas)", f"{total_TE_d*horas_por_dia:.2f}")
colE.metric("σ total (horas)", f"{total_sigma_d*horas_por_dia:.2f}")
colF.metric("TE ajustado (horas)", f"{total_TE_adj_d*horas_por_dia:.2f}")

# ===========================
# Descarga
# ===========================
st.markdown("### 💾 Exportar")
csv = df.to_csv(index=False).encode("utf-8")
st.download_button("📥 Descargar CSV (actividades)", data=csv, file_name="pert_estimacion.csv", mime="text/csv")    