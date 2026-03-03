# pages/3_OCM_PERT_MonteCarlo.py
# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ============================================================
# Utilidades Beta-PERT
# ============================================================
def beta_pert_sample(o, m, p, lamb=4.0, size=1, rng=None):
    """
    Muestra desde una Beta-PERT (esfuerzo/tiempo >= 0).
    lamb=4 recomienda ponderar el 'más probable' (M).
    """
    if rng is None:
        rng = np.random.default_rng()
    o, m, p = float(o), float(m), float(p)
    if p <= o or m < o or m > p:
        # fallback determinista
        return np.full(size, (o + 4*m + p) / 6.0)
    mean = (o + lamb*m + p) / (lamb + 2.0)
    # Forma estandarizada de parámetros alfa/beta
    # alpha = 1 + lamb*(m - o)/(p - o)
    # beta  = 1 + lamb*(p - m)/(p - o)
    alpha = 1.0 + lamb * (m - o) / (p - o)
    beta = 1.0 + lamb * (p - m) / (p - o)
    # muestrear en [0,1] y escalar a [o,p]
    x = rng.beta(alpha, beta, size=size)
    return o + x * (p - o)

def pert_te(o, m, p):
    return (o + 4*m + p) / 6.0

def pert_sigma(o, p):
    return (p - o) / 6.0

# ============================================================
# Datos base: actividades OCM (editable)
# Esfuerzo O/M/P en HORAS y % paralelizable (0..1)
# ============================================================
TIPOS_ACTIVIDAD = ["Estándar/Operativa", "Dependiente de Terceros", "Estratégica/Creativa"]
FASES_OCM = ["FASE 1: Estrategia Inicial", "FASE 2: Workshops y Despliegue", "FASE 3: Contención y Coaching", "FASE 4: Ejecución Recurrente"]

DEFAULT_ACTIVITIES = [
    # FASE 1
    {"Actividad":"Newsletter", "Fase": FASES_OCM[0], "Tipo de Actividad": TIPOS_ACTIVIDAD[0], "M": 8, "Paralelizable": 0.8, "Proyectos": 1},
    {"Actividad":"Playbook Design", "Fase": FASES_OCM[0], "Tipo de Actividad": TIPOS_ACTIVIDAD[2], "M": 40, "Paralelizable": 0.2, "Proyectos": 1},
    {"Actividad":"Training Planning", "Fase": FASES_OCM[0], "Tipo de Actividad": TIPOS_ACTIVIDAD[2], "M": 24, "Paralelizable": 0.4, "Proyectos": 1},
    {"Actividad":"Communication Plan", "Fase": FASES_OCM[0], "Tipo de Actividad": TIPOS_ACTIVIDAD[2], "M": 20, "Paralelizable": 0.4, "Proyectos": 1},
    {"Actividad":"Design Session", "Fase": FASES_OCM[0], "Tipo de Actividad": TIPOS_ACTIVIDAD[1], "M": 16, "Paralelizable": 0.3, "Proyectos": 1},
    # FASE 2
    {"Actividad":"Preparation Workshop", "Fase": FASES_OCM[1], "Tipo de Actividad": TIPOS_ACTIVIDAD[1], "M": 16, "Paralelizable": 0.5, "Proyectos": 1},
    {"Actividad":"Report Workshop", "Fase": FASES_OCM[1], "Tipo de Actividad": TIPOS_ACTIVIDAD[1], "M": 24, "Paralelizable": 0.5, "Proyectos": 1},
    {"Actividad":"Sponsor Stakeholder Mtg", "Fase": FASES_OCM[1], "Tipo de Actividad": TIPOS_ACTIVIDAD[1], "M": 8, "Paralelizable": 0.1, "Proyectos": 1},
    {"Actividad":"Training Execution", "Fase": FASES_OCM[1], "Tipo de Actividad": TIPOS_ACTIVIDAD[0], "M": 40, "Paralelizable": 0.6, "Proyectos": 1},
    {"Actividad":"Communication Execution", "Fase": FASES_OCM[1], "Tipo de Actividad": TIPOS_ACTIVIDAD[0], "M": 32, "Paralelizable": 0.7, "Proyectos": 1},
    # FASE 3
    {"Actividad":"Sponsor Involved & Coaching", "Fase": FASES_OCM[2], "Tipo de Actividad": TIPOS_ACTIVIDAD[2], "M": 30, "Paralelizable": 0.2, "Proyectos": 1},
    {"Actividad":"Containment Strategies", "Fase": FASES_OCM[2], "Tipo de Actividad": TIPOS_ACTIVIDAD[2], "M": 24, "Paralelizable": 0.3, "Proyectos": 1},
    {"Actividad":"Follow-up Communications", "Fase": FASES_OCM[2], "Tipo de Actividad": TIPOS_ACTIVIDAD[0], "M": 16, "Paralelizable": 0.8, "Proyectos": 1},
    # FASE 4
    {"Actividad":"Recurring Comms", "Fase": FASES_OCM[3], "Tipo de Actividad": TIPOS_ACTIVIDAD[0], "M": 16, "Paralelizable": 0.9, "Proyectos": 1},
    {"Actividad":"Recurring Sponsor Mtg", "Fase": FASES_OCM[3], "Tipo de Actividad": TIPOS_ACTIVIDAD[1], "M": 8, "Paralelizable": 0.1, "Proyectos": 1},
    {"Actividad":"Recurring Training", "Fase": FASES_OCM[3], "Tipo de Actividad": TIPOS_ACTIVIDAD[0], "M": 24, "Paralelizable": 0.7, "Proyectos": 1},
]

# ============================================================
# Sidebar: parámetros
# ============================================================
st.sidebar.markdown("## 🧪 OCM PERT — Monte Carlo")

unidad = st.sidebar.selectbox("Unidad de captura", ["Horas","Días"], index=0)
horas_por_dia = st.sidebar.number_input("Horas laborables por día", 1.0, 24.0, 8.0, 0.5)

def to_hours(x): return x if unidad=="Horas" else x*horas_por_dia
def to_days(x):  return x/horas_por_dia if unidad=="Horas" else x

n_iter = st.sidebar.slider("Iteraciones Monte Carlo", min_value=200, max_value=5000, value=1500, step=100)
team_n = st.sidebar.slider("Consultores OCM", min_value=1, max_value=15, value=2, step=1)
team_eff = st.sidebar.slider("Eficiencia de equipo (0–1)", 0.1, 1.0, 0.85, 0.01,
                             help="Eficiencia agregada: coord., handoffs, reuniones")

st.sidebar.markdown("---")
st.sidebar.markdown("### Ajuste por complejidad")

# Factores por complejidad (ajustan ESFUERZO)
factor_defaults = {"Eclipse":1.00, "Galaxy":1.15, "Quantum":1.30, "Nova":1.60}
factors = {}
for k,v in factor_defaults.items():
    factors[k] = st.sidebar.number_input(f"Factor {k}", 0.5, 3.0, float(v), 0.05, key=f"fac_{k}")

source = st.sidebar.radio(
    "Fuente de complejidad",
    ["Sin ajuste","Usar último cálculo","Usar proyecto guardado","Seleccionar manualmente"],
    index=1
)

complexity_label = None
if source == "Usar último cálculo":
    complexity_label = st.session_state.get("complexity_label")
    if complexity_label:
        st.sidebar.success(f"Último: **{complexity_label}**")
    else:
        st.sidebar.warning("No hay cálculo previo en esta sesión.")
        source = "Sin ajuste"

elif source == "Usar proyecto guardado":
    projects = st.session_state.get("projects", [])
    if projects:
        choice = st.sidebar.selectbox(
            "Proyecto",
            [f"{p['name']} — {p['label']}" for p in projects]
        )
        if choice:
            idx = [f"{p['name']} — {p['label']}" for p in projects].index(choice)
            complexity_label = projects[idx]["label"]
    else:
        st.sidebar.warning("No hay proyectos guardados.")
        source = "Sin ajuste"

elif source == "Seleccionar manualmente":
    complexity_label = st.sidebar.selectbox("Clasificación", ["Eclipse","Galaxy","Quantum","Nova"], index=1)

st.sidebar.caption("Ajuste de esfuerzo para reflejar riesgo de adopción y fricción organizacional.")

# ============================================================
# Encabezado y explicación
# ============================================================
st.title("🧪 OCM — PERT + Monte Carlo (duración y esfuerzo)")

with st.expander("¿Qué modelamos aquí?"):
    st.markdown(
        "- Estimamos **esfuerzo OCM** con **PERT (O, M, P)** por actividad y "
        "lo convertimos a **duraciones** considerando **n consultores**, "
        "**eficiencia de equipo** y el **% de paralelización** propio de cada tarea.\n"
        "- El esfuerzo se puede **ajustar por complejidad** del proyecto "
        "(Eclipse/Galaxy/Quantum/Nova) para reflejar incertidumbre y fricción humana, "
        "donde la evidencia sugiere que gestionar bien el cambio mejora el desempeño en "
        "objetivos/tiempos/presupuesto. [3](https://www.proscieurope.co.uk/hubfs/Best-Practices-in-Change-Management-12th-Edition-Executive-Summary.pdf?hsLang=en)\n"
        "- **PERT** usa tres estimaciones y el tiempo esperado **TE=(O+4M+P)/6**, con "
        "**σ=(P−O)/6**, útil cuando la duración es **incierta**. [1](https://projectmanagers.net/pert-formula-examples-pert-calculator/)[2](https://www.calculatoratoz.com/es/pert-expected-time-calculator/Calc-2115)\n"
        "- Puedes seguir usando **CPM/Gantt** para orquestar dependencias y ruta crítica del "
        "programa general; aquí nos enfocamos en el **paquete OCM** con incertidumbre. [4](https://keydifferences.com/difference-between-pert-and-cpm.html)[5](https://crm.org/news/pert-vs-cpm)"
    )

# ============================================================
# Tabla editable de actividades
# ============================================================
st.markdown("### 📋 Actividades OCM (edita M, Tipo, Fase, etc.)")

if "ocm_df" not in st.session_state:
    st.session_state["ocm_df"] = pd.DataFrame(DEFAULT_ACTIVITIES).copy()

edited_df = st.data_editor(
    st.session_state["ocm_df"],
    num_rows="dynamic",
    column_order=("Proyectos", "Actividad", "Fase", "Tipo de Actividad", "M", "Paralelizable"),
    use_container_width=True,
    column_config={
        "Actividad": st.column_config.TextColumn(width="large"),
        "Fase": st.column_config.SelectboxColumn("Fase", options=FASES_OCM, required=True),
        "Tipo de Actividad": st.column_config.SelectboxColumn("Tipo de Actividad", options=TIPOS_ACTIVIDAD, required=True),
        "M": st.column_config.NumberColumn(f"M ({unidad})", help="Estimación de esfuerzo 'Más Probable' en la unidad seleccionada.", min_value=0, format="%d"),
        "Paralelizable": st.column_config.NumberColumn("Paralelizable", help="Fracción del trabajo que puede hacerse en paralelo (0-1).", min_value=0.0, max_value=1.0, format="%.2f"),
        "Proyectos": st.column_config.NumberColumn("Proyectos", help="Nº de proyectos a los que aplica. Multiplica el esfuerzo.", min_value=1, step=1, format="%d"),
    },
    key="ocm_editor"
)

# --- Lógica de cálculo de O y P ---
FACTORES_OP = {
    "Estándar/Operativa":    {"O": 0.90, "P": 1.30},
    "Dependiente de Terceros": {"O": 0.85, "P": 1.75},
    "Estratégica/Creativa":  {"O": 0.80, "P": 2.00},
}

df = edited_df.copy()

# Calcular O y P basado en M y Tipo de Actividad
df["O"] = df.apply(lambda row: row["M"] * FACTORES_OP[row["Tipo de Actividad"]]["O"], axis=1)
df["P"] = df.apply(lambda row: row["M"] * FACTORES_OP[row["Tipo de Actividad"]]["P"], axis=1)

# Ajustar por número de proyectos
df["O"] = df["O"] * df["Proyectos"]
df["M"] = df["M"] * df["Proyectos"]
df["P"] = df["P"] * df["Proyectos"]

st.markdown("#### Estimaciones O/M/P calculadas (en horas)")
st.dataframe(
    df[["Actividad", "Fase", "Proyectos", "O", "M", "P"]].style.format(
        {"O": "{:.1f}", "M": "{:.1f}", "P": "{:.1f}"}
    ),
    use_container_width=True,
    hide_index=True
)

# --- NUEVO: utilidades de PDF ---
def _png_from_fig(fig, scale=2):
    """Devuelve bytes PNG desde un fig de plotly (requiere kaleido)."""
    return fig.to_image(format="png", scale=scale)

def build_pdf_report(
    project_title: str,
    complexity_label: str | None,
    unidad: str,
    horas_por_dia: float,
    team_n: int,
    team_eff: float,
    n_iter: int,
    p50_d: float, p80_d: float, mean_d: float,
    p50_h: float, p80_h: float, mean_h: float,
    eff_mean_h: float, eff_p80_h: float,
    hist_png: bytes, cdf_png: bytes
) -> bytes:
    """Crea el PDF en memoria con ReportLab y devuelve los bytes."""
    from io import BytesIO
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    from reportlab.lib.utils import ImageReader

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    W, H = A4
    x_margin, y_margin = 2*cm, 2*cm
    y = H - y_margin

    # Encabezado
    c.setFont("Helvetica-Bold", 16)
    c.drawString(x_margin, y, "OCM — PERT + Monte Carlo (Reporte)")
    y -= 0.8*cm

    c.setFont("Helvetica", 10)
    c.drawString(x_margin, y, f"Proyecto: {project_title or 's/d'}")
    y -= 0.5*cm
    c.drawString(x_margin, y, f"Complejidad: {complexity_label or 'Sin ajuste'}")
    y -= 0.5*cm
    c.drawString(x_margin, y, f"Unidad: {unidad}  |  Horas/día: {horas_por_dia}")
    y -= 0.5*cm
    c.drawString(x_margin, y, f"Consultores OCM: {team_n}  |  Eficiencia: {team_eff:.2f}  |  Iteraciones: {n_iter}")
    y -= 0.8*cm

    # --- NUEVO: Resumen Ejecutivo ---
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x_margin, y, "Resumen Ejecutivo")
    y -= 0.6*cm
    c.setFont("Helvetica", 10)
    line_height = 0.45 * cm
    text_lines = [
        f"La simulación de {n_iter:,} escenarios indica una probabilidad del 50% (mediana) de completar el paquete OCM en",
        f"aproximadamente {p50_d:.1f} días ({p50_h:.0f} horas).",
        "",
        f"Para un nivel de confianza del 80% (P80), se recomienda planificar una duración de {p80_d:.1f} días ({p80_h:.0f} horas).",
        "",
        f"El esfuerzo total estimado para el equipo de {team_n} consultor(es) se encuentra entre {eff_mean_h:.0f} horas (promedio) y {eff_p80_h:.0f} horas (P80).",
        f"Este reporte asume una eficiencia de equipo del {team_eff*100:.0f}% y una jornada de {horas_por_dia} horas/día."
    ]
    for line in text_lines:
        c.drawString(x_margin, y, line)
        y -= line_height
    y -= 0.4*cm

    # Métricas
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x_margin, y, "Resultados Detallados de la Simulación")
    y -= 0.6*cm
    c.setFont("Helvetica", 10)
    c.drawString(x_margin, y, f"P50:  {p50_d:.2f} días  /  {p50_h:.0f} horas")
    c.drawString(x_margin, y, f"P80:  {p80_d:.2f} días  /  {p80_h:.0f} horas")
    c.drawString(x_margin, y, f"Media:{mean_d:.2f} días  /  {mean_h:.0f} horas")
    c.drawString(x_margin, y, f"Esfuerzo medio: {eff_mean_h:.0f} h   |   Esfuerzo P80: {eff_p80_h:.0f} h")
    y -= 0.8*cm

    # Gráfico 1: Histograma
    try:
        hist_img = ImageReader(BytesIO(hist_png))
        img_w = W - 2*x_margin
        img_h = 7*cm
        c.drawImage(hist_img, x_margin, y - img_h, width=img_w, height=img_h, preserveAspectRatio=True, mask='auto')
        y -= img_h + 0.5*cm
    except Exception:
        c.setFillColor(colors.red)
        c.drawString(x_margin, y, "[No se pudo incrustar el histograma]")
        c.setFillColor(colors.black)
        y -= 0.5*cm

    # Gráfico 2: Curva S
    try:
        cdf_img = ImageReader(BytesIO(cdf_png))
        img_w = W - 2*x_margin
        img_h = 7*cm
        c.drawImage(cdf_img, x_margin, y - img_h, width=img_w, height=img_h, preserveAspectRatio=True, mask='auto')
        y -= img_h + 0.5*cm
    except Exception:
        c.setFillColor(colors.red)
        c.drawString(x_margin, y, "[No se pudo incrustar la Curva S]")
        c.setFillColor(colors.black)
        y -= 0.5*cm

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.getvalue()

# ============================================================
# Simulación
# ============================================================
st.markdown("### ▶ Ejecutar Simulación")
run = st.button("Calcular Monte Carlo")

if run:
    rng = np.random.default_rng(12345)
    n = len(df)

    # --- Generación dinámica de dependencias por fase ---
    fases_ordenadas = sorted(list(df["Fase"].unique()), key=lambda x: FASES_OCM.index(x))
    act_por_fase = {fase: df[df["Fase"] == fase].index.tolist() for fase in fases_ordenadas}

    edges = []
    for i in range(len(fases_ordenadas) - 1):
        fase_predecesora = fases_ordenadas[i]
        fase_sucesora = fases_ordenadas[i+1]
        for pred_idx in act_por_fase[fase_predecesora]:
            for succ_idx in act_por_fase[fase_sucesora]:
                edges.append((pred_idx, succ_idx))

    # Preparar arrays
    O = to_hours(df["O"].values.astype(float))
    M = to_hours(df["M"].values.astype(float))
    P = to_hours(df["P"].values.astype(float))
    PAR = df["Paralelizable"].values.clip(0,1)

    # Ajuste por complejidad (en ESFUERZO)
    if complexity_label in factors:
        adj = factors[complexity_label]
    else:
        adj = 1.0

    # Muestreos
    samples_effort = np.vstack([
        beta_pert_sample(O[i], M[i], P[i], size=n_iter, rng=rng) * adj
        for i in range(n)
    ])  # shape: (n, n_iter) en HORAS

    # Capacidad efectiva por actividad (en consultores)
    # Regla: eff_team_i = 1 + (team_n - 1) * PAR[i] * team_eff
    eff_team = 1.0 + (team_n - 1.0) * PAR * team_eff
    eff_team = np.maximum(eff_team, 1.0)  # al menos 1

    # Convertir ESFUERZO a DURACIÓN por actividad (en DÍAS)
    dur_days = samples_effort / (eff_team[:,None] * horas_por_dia)

    # Programar con dependencias: cálculo de EF (Early Finish) por iteración
    # Si no quieres dependencias, usa project_duration = dur_days.sum(axis=0)
    preds = {i: [] for i in range(n)}
    for u,v in edges:
        if u < n and v < n: preds[v].append(u)

    # Topo order trivial (asumimos orden natural y edges consistentes)
    order = list(range(n))
    EF = np.zeros((n, n_iter))
    for i in order:
        if preds[i]:
            ES_i = np.max(EF[preds[i], :], axis=0)  # earliest start
        else:
            ES_i = 0.0
        EF[i,:] = ES_i + dur_days[i,:]

    project_duration_days = np.max(EF, axis=0)
    total_effort_hours = np.sum(samples_effort, axis=0)

    # Estadísticos
    p50_d = float(np.percentile(project_duration_days, 50))
    p80_d = float(np.percentile(project_duration_days, 80))
    mean_d = float(np.mean(project_duration_days))

    p50_h = p50_d * horas_por_dia
    p80_h = p80_d * horas_por_dia
    mean_h = mean_d * horas_por_dia

    # ======= Resultados =======
    st.markdown("### 📈 Distribución de duración (días)")
    fig = px.histogram(x=project_duration_days, nbins=40, opacity=0.8)
    fig.add_vline(p50_d, line_width=2, line_dash="dash", line_color="green")
    fig.add_vline(p80_d, line_width=2, line_dash="dash", line_color="orange")
    fig.update_layout(xaxis_title="Duración del paquete OCM (días)", yaxis_title="Frecuencia")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 📈 Curva S (CDF)")
    xs = np.sort(project_duration_days)
    ys = np.arange(1, len(xs)+1) / len(xs)
    fig2 = px.line(x=xs, y=ys)
    fig2.add_vline(p50_d, line_width=2, line_dash="dash", line_color="green")
    fig2.add_vline(p80_d, line_width=2, line_dash="dash", line_color="orange")
    fig2.update_layout(xaxis_title="Duración (días)", yaxis_title="Probabilidad acumulada")
    st.plotly_chart(fig2, use_container_width=True)

    # Métricas
    c1, c2, c3 = st.columns(3)
    c1.metric("P50 (días / horas)", f"{p50_d:.2f} / {p50_h:.0f}")
    c2.metric("P80 (días / horas)", f"{p80_d:.2f} / {p80_h:.0f}")
    c3.metric("Media (días / horas)", f"{mean_d:.2f} / {mean_h:.0f}")

    # Esfuerzo (útil para dimensionar consultores)
    st.markdown("### 👥 Esfuerzo total (para dimensionamiento)")
    eff_mean_h = float(np.mean(total_effort_hours))
    eff_p80_h  = float(np.percentile(total_effort_hours, 80))
    e1, e2 = st.columns(2)
    e1.metric("Esfuerzo medio (horas)", f"{eff_mean_h:.0f}")
    e2.metric("Esfuerzo P80 (horas)", f"{eff_p80_h:.0f}")
    st.caption("El esfuerzo OCM sirve para estimar cuántos consultores necesitas y/ó su dedicación.")

    # Descarga
    st.markdown("### 💾 Descargar simulación (csv)")
    out = pd.DataFrame({
        "duration_days": project_duration_days,
        "duration_hours": project_duration_days * horas_por_dia,
        "total_effort_hours": total_effort_hours
    })
    st.download_button(
        "📥 Descargar resultados",
        data=out.to_csv(index=False).encode("utf-8"),
        file_name="ocm_pert_montecarlo.csv",
        mime="text/csv"
    )

# --- NUEVO: Exportar a PDF ---
try:
    hist_png = _png_from_fig(fig, scale=2)
    cdf_png  = _png_from_fig(fig2, scale=2)

    pdf_bytes = build_pdf_report(
        project_title=st.session_state.get("current_project_name",""),
        complexity_label=complexity_label,
        unidad=unidad, horas_por_dia=horas_por_dia,
        team_n=team_n, team_eff=team_eff, n_iter=n_iter,
        p50_d=p50_d, p80_d=p80_d, mean_d=mean_d,
        p50_h=p50_h, p80_h=p80_h, mean_h=mean_h,
        eff_mean_h=eff_mean_h, eff_p80_h=eff_p80_h,
        hist_png=hist_png, cdf_png=cdf_png
    )

    st.download_button(
        "🖨️ Descargar reporte PDF",
        data=pdf_bytes,
        file_name="OCM_PERT_MonteCarlo.pdf",
        mime="application/pdf"
    )
except Exception as e:
    st.warning("Para exportar PDF, verifica que `kaleido` y `reportlab` estén instalados en tu app.")

else:
    st.info("Configura parámetros y pulsa **Calcular Monte Carlo**.")