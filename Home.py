# Home.py (portada)
import streamlit as st

st.set_page_config(
    page_title="Project Calculators",   # ← título mostrado en la navegación
    page_icon="🛰️",
    layout="wide",
)

st.title("🛰️ Project Calculators")
st.markdown("""
Bienvenido. Usa el menú **Pages** para navegar:
- Calculadora de **Complejidad**. Evalúa 8 dimensiones (1–7), genera radar por clasificación y sugiere Gestión del Cambio.
- **PERT 3 puntos**. PERT modela incertidumbre con tres estimaciones (O, M, P) y es ideal para proyectos no repetitivos o con alta variabilidad (I+D, innovación).
- **OCM — PERT + Monte Carlo**. Cálculo de las actividades OCM, que utiliza rangos de incertidumbre humana (PERT) y simulaciones de escenarios (Monte Carlo).
""")

# (opcional) enlaces rápidos si está disponible en tu versión:
try:
    st.page_link("pages/1_Complexity_Calculator.py", label="Ir a Calculadora de Complejidad", icon="🧭")
    st.page_link("pages/2_PERT_Three_Point.py", label="Ir a PERT 3 puntos", icon="📊")
    st.page_link("pages/3_OCM_PERT_MonteCarlo.py", label="Ir a OCM — PERT + Monte Carlo", icon="🧪")
except Exception:
    pass