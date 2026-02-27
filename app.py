# app.py
# -*- coding: utf-8 -*-
import streamlit as st

# Configuración global de la app (solo aquí)
st.set_page_config(
    page_title="Project Calculators",
    page_icon="🛰️",
    layout="wide",
)

st.title("🛰️ Project Calculators")
st.markdown("""
Bienvenido. Aquí encontrarás dos herramientas:

1. **Calculadora de Complejidad de Proyectos** (perfil 1–7 por 8 dimensiones, radar por clasificación y recomendación de Gestión del Cambio).
2. **Calculadora PERT (3 puntos)** para estimación de tiempos por actividad.

Usa el **menú lateral** para navegar o los accesos rápidos de abajo.
""")

# Accesos rápidos (si tu versión de Streamlit soporta st.page_link, úsalo)
try:
    st.page_link("pages/1_Complexity_Calculator.py", label="Ir a Calculadora de Complejidad", icon="🧭")
    st.page_link("pages/2_PERT_Three_Point.py", label="Ir a PERT 3 puntos", icon="📊")
except Exception:
    st.markdown("- 👉 Calculadora de Complejidad: ve al menú lateral **Pages**")
    st.markdown("- 👉 PERT 3 puntos: ve al menú lateral **Pages**")

st.divider()
st.caption("Tip: primero calcula la complejidad. La página PERT puede (opcionalmente) ajustar el TE según la clasificación.")