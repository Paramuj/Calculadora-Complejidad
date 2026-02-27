# pages/1_Complexity_Calculator.py
# -*- coding: utf-8 -*-
import json
from datetime import datetime
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.io as pio
import streamlit as st

pio.templates.default = "plotly"

DIMENSIONES = [
    "Tamaño del cambio",
    "Impacto cultural / grado de cambio",
    "Complejidad técnica",
    "Nivel de riesgo",
    "Alineación y apoyo de liderazgo",
    "Integraciones / terceros",
    "Gobernanza y patrocinio",
    "Urgencia / presión de tiempo",
]

# Clasificación y colores
CLASIFICACION = [
    (0,   2.0, "Eclipse", "Baja complejidad"),
    (2.0, 3.5, "Galaxy",  "Complejidad moderada"),
    (3.5, 5.0, "Quantum", "Complejidad alta"),
    (5.0, 7.1, "Nova",    "Complejidad muy alta"),
]
CLASIF_COLOR = {
    "Eclipse": "#2E7D32", "Galaxy": "#F9A825",
    "Quantum": "#EF6C00", "Nova": "#C62828",
    "Sin datos": "#607D8B"
}

QUESTION_BANK = {
    "Tamaño del cambio": [
        {"texto": "Usuarios impactados por el cambio",
         "opciones": {"Menos de 100": 1, "100–500": 3, "501–2,000": 5, "Más de 2,000": 7}, "peso": 1.0},
        {"texto": "Número de áreas o equipos involucrados",
         "opciones": {"1": 1, "2–3": 3, "4–6": 5, "Más de 6": 7}, "peso": 1.0},
        {"texto": "Cambios en procesos core del negocio",
         "opciones": {"No": 1, "Parciales": 4, "Sí, significativos": 7}, "peso": 1.0},
    ],
    "Impacto cultural / grado de cambio": [
        {"texto": "Cambios en roles y responsabilidades",
         "opciones": {"Nulos": 1, "Algunos": 4, "Muchos / reconfiguración": 7}, "peso": 1.0},
        {"texto": "Necesidad de capacitación/acompañamiento",
         "opciones": {"Baja": 2, "Media": 4, "Alta": 6, "Intensiva": 7}, "peso": 1.0},
        {"texto": "Resistencia esperada al cambio",
         "opciones": {"Mínima": 1, "Moderada": 4, "Alta": 7}, "peso": 1.0},
    ],
    "Complejidad técnica": [
        {"texto": "Número de integraciones",
         "opciones": {"0–1": 1, "2–3": 3, "4–6": 5, "Más de 6": 7}, "peso": 1.0},
        {"texto": "Tecnologías nuevas para el equipo",
         "opciones": {"No": 1, "Algunas": 4, "Varias / desconocidas": 7}, "peso": 1.0},
        {"texto": "Dependencias con otros proyectos/equipos",
         "opciones": {"Bajas": 2, "Medias": 4, "Altas": 6, "Críticas": 7}, "peso": 1.0},
    ],
    "Nivel de riesgo": [
        {"texto": "Riesgos técnicos identificados",
         "opciones": {"Bajos": 2, "Medios": 4, "Altos": 6, "Muy altos": 7}, "peso": 1.0},
        {"texto": "Riesgos de negocio (regulatorio, mercado, ingresos)",
         "opciones": {"Bajos": 2, "Medios": 4, "Altos": 6, "Muy altos": 7}, "peso": 1.0},
        {"texto": "Riesgos de adopción de usuarios",
         "opciones": {"Bajos": 2, "Medios": 4, "Altos": 6, "Muy altos": 7}, "peso": 1.0},
    ],
    "Alineación y apoyo de liderazgo": [
        {"texto": "Claridad de objetivos y alcance",
         "opciones": {"Muy claros": 1, "Parcialmente claros": 4, "Difusos / cambiantes": 7}, "peso": 1.0},
        {"texto": "Compromiso y disponibilidad del sponsor",
         "opciones": {"Alto": 1, "Medio": 4, "Bajo": 7}, "peso": 1.0},
        {"texto": "Alineación entre áreas directivas",
         "opciones": {"Alta": 1, "Media": 4, "Baja / conflictos": 7}, "peso": 1.0},
    ],
    "Integraciones / terceros": [
        {"texto": "Número de proveedores/partners involucrados",
         "opciones": {"0–1": 1, "2–3": 3, "4–5": 5, "Más de 5": 7}, "peso": 1.0},
        {"texto": "Criticidad de terceros para el éxito",
         "opciones": {"Baja": 1, "Media": 4, "Alta / dependencia total": 7}, "peso": 1.0},
        {"texto": "Nivel de coordinación contractual/SLAs",
         "opciones": {"Simple": 1, "Moderado": 4, "Complejo": 7}, "peso": 1.0},
    ],
    "Gobernanza y patrocinio": [
        {"texto": "Modelo de decisión y escalamiento",
         "opciones": {"Claro y rápido": 1, "Parcialmente claro": 4, "Confuso / lento": 7}, "peso": 1.0},
        {"texto": "Roles y ownership definidos",
         "opciones": {"Sí": 1, "Parcialmente": 4, "No": 7}, "peso": 1.0},
        {"texto": "Frecuencia/efectividad de los comités",
         "opciones": {"Adecuada": 1, "Irregular": 4, "Insuficiente": 7}, "peso": 1.0},
    ],
    "Urgencia / presión de tiempo": [
        {"texto": "Horizonte para la entrega",
         "opciones": {"≥ 6 meses": 1, "3–6 meses": 4, "≤ 3 meses": 7}, "peso": 1.0},
        {"texto": "Flexibilidad de alcance / fechas",
         "opciones": {"Alta": 1, "Media": 4, "Baja / fija": 7}, "peso": 1.0},
        {"texto": "Disponibilidad de recursos para el plan",
         "opciones": {"Suficientes": 1, "Limitados": 4, "Críticos": 7}, "peso": 1.0},
    ],
}

def calcular_puntaje_dimension(respuestas_dimension):
    if not respuestas_dimension: return np.nan
    pesos = [p["peso"] for p in respuestas_dimension]
    vals  = [p["valor"] for p in respuestas_dimension]
    return float(np.average(vals, weights=pesos))

def clasificar_promedio(prom):
    for lo, hi, etiqueta, desc in CLASIFICACION:
        if lo < prom <= hi: return etiqueta, desc
    return "Sin datos", ""

def rgba_from_hex(hex_color, alpha=0.45):
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16); g = int(hex_color[2:4], 16); b = int(hex_color[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

def palette_for_theme(tema: str):
    if tema == "Oscuro":
        return {"paper_bg":"rgba(20,20,20,1)","plot_bg":"rgba(20,20,20,1)","grid":"rgba(255,255,255,0.15)","axis":"rgba(255,255,255,0.92)"}
    else:
        return {"paper_bg":"rgba(255,255,255,1)","plot_bg":"rgba(255,255,255,1)","grid":"rgba(0,0,0,0.15)","axis":"rgba(0,0,0,0.88)"}

def generar_radar(scores_dict, etiqueta, tema):
    pal = palette_for_theme(tema)
    orden = DIMENSIONES
    r = [scores_dict.get(dim, None) for dim in orden]
    df = pd.DataFrame({"Dimensión": orden, "Puntaje": r})
    color = CLASIF_COLOR.get(etiqueta, "#2196F3")
    fig = px.line_polar(df, r="Puntaje", theta="Dimensión", line_close=True, range_r=[0,7], markers=True)
    fig.update_traces(fill="toself", line=dict(color=color, width=3),
                      marker=dict(color=color, size=6),
                      fillcolor=rgba_from_hex(color, 0.40))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(showline=True, dtick=1, gridcolor=pal["grid"], tickfont=dict(color=pal["axis"])),
            angularaxis=dict(gridcolor=pal["grid"], tickfont=dict(color=pal["axis"]))
        ),
        paper_bgcolor=pal["paper_bg"], plot_bgcolor=pal["plot_bg"], font=dict(color=pal["axis"]),
        showlegend=False, height=560, margin=dict(l=20, r=20, t=60, b=20),
        title=f"Perfil de complejidad (1–7) — {etiqueta}",
    )
    fig.add_annotation(x=0.01, y=1.12, xref="paper", yref="paper",
        text=f"Clasificación: <b style='color:{color}'>{etiqueta}</b>",
        showarrow=False, font=dict(color=pal["axis"], size=14),
        bgcolor=rgba_from_hex(color, 0.15), bordercolor=color, borderwidth=1, borderpad=4)
    return fig

# ===== Sidebar =====
with st.sidebar:
    st.markdown("## 🛰️ Calculadora de Complejidad")
    st.write("Evalúa 8 dimensiones (1–7), genera radar por **clasificación** y sugiere **Gestión del Cambio**.")
    st.markdown("### Apariencia")
    tema = st.radio("Tema del gráfico", options=["Claro","Oscuro"], index=0)
    st.markdown("### Colores")
    st.caption("Eclipse=Verde, Galaxy=Ámbar, Quantum=Naranja, Nova=Rojo")

st.title("🛰️ Calculadora de Complejidad de Proyectos")
st.caption("Formulario → 8 dimensiones (1–7) → Radar coloreado + recomendación OCM + exportaciones.")

st.markdown("### Información del proyecto")
colA, colB = st.columns(2)
with colA: nombre_proyecto = st.text_input("Nombre del proyecto", value="")
with colB: responsable     = st.text_input("Responsable", value="")

st.markdown("---"); st.markdown("### Formulario")

respuestas_crudas = {}
respuestas_puntuadas = {dim: [] for dim in DIMENSIONES}

with st.form(key="formulario_complejidad"):
    for dim in DIMENSIONES:
        st.subheader(dim)
        for idx, q in enumerate(QUESTION_BANK[dim]):
            key = f"{dim}__{idx}"
            opciones = list(q["opciones"].keys())
            sel = st.selectbox(q["texto"], options=["— Selecciona —"]+opciones, index=0, key=key)
            respuestas_crudas[key] = sel
            if sel != "— Selecciona —":
                respuestas_puntuadas[dim].append({"pregunta": q["texto"], "valor": q["opciones"][sel], "peso": q["peso"], "respuesta": sel})
        st.markdown("")
    enviado = st.form_submit_button("Calcular complejidad")

if enviado:
    scores = {dim: calcular_puntaje_dimension(respuestas_puntuadas[dim]) for dim in DIMENSIONES}
    vals = [v for v in scores.values() if pd.notna(v)]
    if vals:
        promedio = float(np.mean(vals)); etiqueta, desc = clasificar_promedio(promedio)
    else:
        promedio = np.nan; etiqueta, desc = "Sin datos", ""

    col1, col2 = st.columns([1,1])
    with col1:
        st.markdown("#### Perfil de complejidad")
        fig = generar_radar(scores, etiqueta, tema)
        st.plotly_chart(fig, use_container_width=True)
        try:
            png_bytes = fig.to_image(format="png", scale=2)
            st.download_button("📷 Descargar radar (PNG)", data=png_bytes, file_name="perfil_complejidad.png", mime="image/png")
        except Exception:
            st.warning("Para exportar PNG instala 'kaleido'.")

    with col2:
        st.markdown("#### Resumen")
        df_scores = pd.DataFrame({"Dimensión": DIMENSIONES, "Puntaje (1–7)": [scores[d] for d in DIMENSIONES]})
        st.dataframe(df_scores.set_index("Dimensión"), use_container_width=True, height=370)
        color = CLASIF_COLOR.get(etiqueta, "#607D8B")
        st.metric("Promedio global", f"{promedio:.2f}" if pd.notna(promedio) else "—")
        st.markdown(f"<b>Clasificación:</b> <span style='color:{color};font-weight:700'>{etiqueta}</span> — <i>{desc}</i>", unsafe_allow_html=True)

    # --- Recomendación OCM (simple y accionable) ---
    st.markdown("---"); st.markdown("### Gestión del Cambio (OCM) — recomendación")
    def recomendacion_cm(scores, promedio):
        tc = scores.get("Tamaño del cambio", np.nan)
        ic = scores.get("Impacto cultural / grado de cambio", np.nan)
        al = scores.get("Alineación y apoyo de liderazgo", np.nan)
        ur = scores.get("Urgencia / presión de tiempo", np.nan)
        nr = scores.get("Nivel de riesgo", np.nan)
        disparadores = []
        if not np.isnan(ic) and ic >= 4: disparadores.append("Impacto cultural ≥ 4")
        if not np.isnan(tc) and tc >= 4: disparadores.append("Tamaño del cambio ≥ 4")
        if not np.isnan(al) and al >= 5: disparadores.append("Baja alineación de liderazgo (≥5)")
        if not np.isnan(ur) and ur >= 6: disparadores.append("Alta presión de tiempo (≥6)")
        if not np.isnan(nr) and nr >= 5: disparadores.append("Riesgo elevado (≥5)")
        etiqueta_, _ = clasificar_promedio(promedio)
        if etiqueta_ in ("Quantum","Nova"):
            nivel = "Requerido"
            detalle = "OCM formal: stakeholders, comunicaciones, capacitación, readiness y KPIs."
        elif etiqueta_ == "Galaxy":
            if disparadores:
                nivel = "Requerido"; detalle = "CM requerido por disparadores: " + "; ".join(disparadores)
            else:
                nivel = "Recomendado"; detalle = "CM recomendado (comms + training focalizado)."
        elif etiqueta_ == "Eclipse":
            if disparadores:
                nivel = "Recomendado"; detalle = "CM recomendado por disparadores: " + "; ".join(disparadores)
            else:
                nivel = "Opcional"; detalle = "CM opcional; comunicación informativa."
        else:
            nivel = "Indeterminado"; detalle = "Complete el formulario."
        return nivel, detalle, disparadores

    nivel, detalle, disparadores = recomendacion_cm(scores, promedio)
    color_badge = {"Requerido":"#C62828","Recomendado":"#EF6C00","Opcional":"#2E7D32","Indeterminado":"#607D8B"}.get(nivel,"#607D8B")
    st.markdown(f"<div style='padding:10px;border-radius:8px;border:1px solid {color_badge}33'>"
                f"<span style='background:{color_badge};color:white;padding:4px 8px;border-radius:6px;font-weight:700;'> {nivel} </span>"
                f"<div style='margin-top:8px'>{detalle}</div></div>", unsafe_allow_html=True)
    if disparadores: st.caption("Disparadores detectados: " + " · ".join(disparadores))

    # --- Descargas ---
    st.markdown("---"); st.markdown("### Descargas")
    csv_df = pd.DataFrame({"Dimension": DIMENSIONES, "Puntaje": [scores[d] for d in DIMENSIONES]})
    st.download_button("📥 Puntajes por dimensión (CSV)", data=csv_df.to_csv(index=False).encode("utf-8"),
                       file_name="puntajes_complejidad.csv", mime="text/csv")
    salida = {
        "proyecto": nombre_proyecto, "responsable": responsable,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "scores_por_dimension": scores, "promedio": float(promedio) if pd.notna(promedio) else None,
        "clasificacion": {"etiqueta": etiqueta, "descripcion": desc}, "tema_grafico": tema,
    }
    st.download_button("📥 Detalle completo (JSON)", data=json.dumps(salida, ensure_ascii=False, indent=2).encode("utf-8"),
                       file_name="detalle_complejidad.json", mime="application/json")

    # --- Guardar proyecto para usar en PERT ---
    st.markdown("---"); st.markdown("### Guardar este proyecto")
    if "projects" not in st.session_state: st.session_state["projects"] = []
    new_name = st.text_input("Nombre para guardar (catálogo interno)", value=nombre_proyecto or f"Proyecto {datetime.now():%Y-%m-%d %H:%M}")
    if st.button("💾 Guardar proyecto"):
        st.session_state["projects"].append({
            "name": new_name.strip() or f"Proyecto {len(st.session_state['projects'])+1}",
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "scores": scores, "avg": float(promedio) if pd.notna(promedio) else None,
            "label": etiqueta
        })
        st.success(f"Proyecto guardado: {new_name}")

    # Compartir “último cálculo” con otras páginas
    st.session_state["current_project_name"] = new_name
    st.session_state["complexity_label"] = etiqueta
    st.session_state["complexity_score"] = float(promedio) if pd.notna(promedio) else None

else:
    st.info("Completa el formulario y presiona **Calcular complejidad** para ver resultados.")
