# 🛰️ Project Calculators

Herramientas avanzadas para estimación, complejidad y gestión del cambio (OCM)
Project Calculators es un conjunto de herramientas interactivas desarrolladas en Streamlit para apoyar la estimación, planeación y gestión de proyectos —con un enfoque especial en Gestión del Cambio (OCM), análisis de complejidad, estimación PERT y simulaciones con Monte Carlo.

El objetivo es brindar estimaciones realistas, anticipar riesgos humanos y organizacionales, y ofrecer una guía sólida para dimensionar actividades, recursos y tiempos del componente OCM de un proyecto.

## 🧭 Contenido del proyecto

Este repositorio contiene tres calculadoras principales:

### 1️⃣ Calculadora de Complejidad del Proyecto

Evalúa un proyecto en 8 dimensiones fundamentales:

- Tamaño del cambio
- Impacto cultural
- Complejidad técnica
- Nivel de riesgo
- Gobernanza
- Soporte de liderazgo
- Integraciones
- Urgencia / presión de tiempo

Incluye:

- Encuesta interactiva (Likert 1–7)
- Gráfico radar con color por nivel de complejidad

Clasificación automática:

🟢 Eclipse (Baja)
🟡 Galaxy (Media)
🟠 Quantum (Alta)
🔴 Nova (Muy alta)

- Recomendación de Gestión del Cambio según la complejidad
- Guardado de proyectos para reutilización
- Exportación: CSV, JSON, PNG
- Control de tema gráfico (Claro / Oscuro)

### 2️⃣ Calculadora PERT de 3 puntos

Implementa la fórmula estándar PERT:

- TE = (O + 4M + P) / 6  
- σ  = (P - O) / 6

Características:

- Estimación por actividad
- Resultados agregados (TE total y σ total)
- Soporte para Horas ⇄ Días, configurable
- Ajuste opcional basado en la complejidad del proyecto
- Exportación a CSV


### 3️⃣ OCM — PERT + Simulación Monte Carlo

Un módulo especializado para estimar de manera robusta el paquete de trabajo de Gestión del Cambio (OCM):

🔹 Incluye actividades típicas de OCM, como:

- Estrategia y plan
- Análisis de impactos
- Stakeholders
- Plan de comunicaciones
- Plan de capacitación
- Readiness
- Ejecución comunicaciones + training
- Refuerzo

🔹 Modela:

- Esfuerzo en O/M/P
- Ajuste por complejidad
- % de paralelización de cada actividad
- Número de consultores
- Eficiencia de equipo y retornos decrecientes
- Dependencias naturales entre actividades

🔹 Simulación Monte Carlo

- 200–5000 iteraciones
- Distribución Beta‑PERT
- P50, P80, media
- Histograma y Curva S
- Exportación: CSV, PDF profesional con gráficos y métricas


## 🗂️ Estructura del repositorio

```
project-root/
│
├── Project_Calculators.py        # Home
│
├── pages/
│   ├── 1_Complexity_Calculator.py
│   ├── 2_PERT_Three_Point.py
│   └── 3_OCM_PERT_MonteCarlo.py
│
├── requirements.txt
└── README.md
```

### 🚀 Cómo ejecutar localmente
1. Crear entorno virtual
```
python -m venv
.venvsource .venv/bin/activate       # Windows: .venv\Scripts\activate
```
2. Instalar dependencias
```
pip install -r requirements.txt
```
3. Ejecutar la aplicación
```
streamlit run Project_Calculators.py
```
5. Abrir en el navegador

http://localhost:8501


### 🌐 Cómo desplegar en Streamlit Cloud

- Sube este repositorio a GitHub
- Entra a: https://share.streamlit.io
- Crea una nueva app
- Selecciona repo + branch
- Archivo principal: Project_Calculators.py

¡Listo! El menú “Pages” mostrará automáticamente las tres calculadoras.

### 🧠 Fundamentos técnicos

🔹 PERT (Project Evaluation and Review Technique)

Basado en O/M/P para modelar incertidumbre.

Ideal cuando no existen datos históricos consistentes.

🔹 Monte Carlo

Simula cientos o miles de escenarios posibles para entregar estimaciones probabilísticas, no deterministas:

- P50 = estimación realista
- P80 = estimación conservadora
- Curva S para análisis de riesgo

🔹 Por qué integrar OCM

La investigación de Prosci demuestra que la efectividad en la gestión del cambio mejora significativamente la probabilidad de que un proyecto:

- Cumpla sus objetivos
- Termine en tiempo
- Termine en presupuesto

Por ello, la complejidad del proyecto ajusta el esfuerzo OCM en la simulación.

### 🎨 Estilos y diseño

- Interfaz limpia
- Colores por clasificación
- Modo Claro/Oscuro para gráficos
- Exportación profesional a PDF
- Código modular y legible

### 🛣️ Roadmap

- PDF para la Calculadora de Complejidad
- Reporte ejecutivo completo (OCM + Complejidad + PERT)
- Integración con Gantt automatizado
- Persistencia de proyectos en archivo/DB
- Roles con distintas productividades (Sr/Jr)

### 📬 Contacto

¿Ideas nuevas? ¿Mejoras? ¿Quieres usarlo en tu organización?

### Pablo Ramírez Mujica

📧 [e-mail](mailto:pablormujica@gmail.com)

🔗 [LinkedIn](https://www.linkedin.com/in/pablormujica?utm_source=share_via&utm_content=profile&utm_medium=member_android)

### 📝 Licencia

Este proyecto está bajo licencia MIT — utilízalo, modifícalo y mejóralo libremente.
