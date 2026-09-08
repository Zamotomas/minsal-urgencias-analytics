import warnings
import pandas as pd
import plotly.express as px
import psycopg2
import streamlit as st



# 1. Configuración inicial de la página
st.set_page_config(
    page_title="MINSAL Analytics | Observatorio de Urgencias",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Inyección de Estilos CSS Avanzados (Diseño tipo SaaS / Landing Page)
st.markdown(
    """
    <style>
    /* Estilos globales */
    .stApp {
        background-color: #f8fafc;
        font-family: 'Inter', sans-serif;
    }
    
    /* Hero Banner Principal */
    .hero-container {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
        color: white;
        padding: 3rem 2.5rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
        box-shadow: 0 20px 25px -5px rgba(15, 23, 42, 0.15);
    }
    .hero-badge {
        background-color: rgba(59, 130, 246, 0.2);
        color: #60a5fa;
        padding: 0.35rem 0.85rem;
        border-radius: 50px;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .hero-title {
        font-size: 2.5rem;
        font-weight: 800;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
        color: #ffffff;
    }
    .hero-subtitle {
        font-size: 1.1rem;
        color: #94a3b8;
        font-weight: 400;
        max-width: 800px;
        line-height: 1.5;
    }

    /* Tarjetas de Historia / Contenido */
    .story-card {
        background-color: #ffffff;
        padding: 1.75rem;
        border-radius: 0.75rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
        margin-bottom: 1.5rem;
    }
    .story-text {
        font-size: 1.02rem;
        line-height: 1.7;
        color: #334155;
    }

    /* Cajas de Insights Estratégicos */
    .insight-box {
        background-color: #eff6ff;
        border-left: 4px solid #2563eb;
        padding: 1.25rem;
        border-radius: 0 0.5rem 0.5rem 0;
        color: #1e40af;
        font-size: 0.95rem;
        line-height: 1.6;
        margin-top: 1rem;
        margin-bottom: 2rem;
    }
    
    /* Ocultar elementos nativos molestos de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""",
    unsafe_allow_html=True,
)

# Configuración segura de base de datos con st.secrets
DB_CONFIG = {
    "dbname": st.secrets["postgres"]["dbname"],
    "user": st.secrets["postgres"]["user"],
    "password": st.secrets["postgres"]["password"],
    "host": st.secrets["postgres"]["host"],
    "port": st.secrets["postgres"]["port"],
    "client_encoding": "utf8",
}


@st.cache_data
def ejecutar_consulta(query, params=None):
  conn = psycopg2.connect(**DB_CONFIG)
  conn.set_client_encoding("UTF8")
  df = pd.read_sql(query, conn, params=params)
  conn.close()
  return df


# Función para extraer métricas globales del dataset
@st.cache_data
def cargar_metadatos_globales():
  q = """
    SELECT 
        COUNT(*) as total_filas, 
        SUM(total_atenciones) as total_atenciones_acumuladas,
        MIN(anio) as anio_min,
        MAX(anio) as anio_max
    FROM atenciones_urgencia;
    """
  df = ejecutar_consulta(q)
  if not df.empty:
    return (
        int(df.iloc[0]["total_filas"]),
        int(df.iloc[0]["total_atenciones_acumuladas"]),
        int(df.iloc[0]["anio_min"]),
        int(df.iloc[0]["anio_max"]),
    )
  return 0, 0, 2021, 2024


total_filas, total_atenciones, anio_min, anio_max = cargar_metadatos_globales()

# --- 3. BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
  st.image("https://img.icons8.com/color/96/hospital-3.png", width=70)
  st.markdown("### **MINSAL OpenData**")
  st.markdown(
      "Plataforma interactiva de inteligencia sanitaria basada en registros"
      " masivos de urgencias (SADU)."
  )
  st.markdown("---")
  st.markdown("**Stack Tecnológico:**")
  st.markdown("* 🐘 **PostgreSQL** (Almacenamiento relacional)")
  st.markdown("* ⚡ **FastAPI & DuckDB** (Pipeline ETL y API)")
  st.markdown("* 🎨 **Streamlit & Plotly** (Visualización interactiva)")
  st.markdown("---")
  st.info(
      "💡 **Nota:** Utiliza el explorador de datos al final para exportar"
      " reportes personalizados."
  )

# --- 4. HERO BANNER PRINCIPAL ---
st.markdown(
    """
    <div class="hero-container">
        <span class="hero-badge">Observatorio de Salud Pública • Chile</span>
        <div class="hero-title">Radiografía a las Urgencias Sanitarias</div>
        <div class="hero-subtitle">
            Análisis avanzado del comportamiento asistencial en la Red Pública de Salud. 
            Una solución integral de ingeniería y visualización de datos diseñada para la toma de decisiones estratégicas.
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

# --- INTRODUCCIÓN Y ESCALA DEL DATASET ---
st.markdown("### 📊 Sobre los Datos y la Fuente")
st.markdown(
    """
    <div class='story-card story-text'>
    Este observatorio procesa y analiza los registros públicos oficiales del <b>Departamento de Estadísticas e Información de Salud (DEIS)</b> 
    del Ministerio de Salud de Chile (MINSAL). La base de datos centraliza el <b>Sistema de Atención de Urgencia (SADU)</b>, 
    permitiendo auditar la volumetría, estacionalidad y demografía de la demanda asistencial en todo el territorio nacional.
    </div>
""",
    unsafe_allow_html=True,
)

# Métricas de escala globales en columnas
col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
  st.metric(
      label="📂 Registros Procesados (Filas DB)",
      value=f"{total_filas:,}".replace(",", "."),
      help="Número total de filas procesadas en PostgreSQL",
  )
with col_m2:
  st.metric(
      label="🏥 Atenciones Totales Analizadas",
      value=f"{total_atenciones:,}".replace(",", "."),
      help="Suma acumulada de pacientes atendidos",
  )
with col_m3:
  st.metric(
      label="📅 Ventana Temporal Cubierta",
      value=f"{anio_min} - {anio_max}",
      help="Rango de años evaluados en el sistema",
  )

st.markdown("<br>", unsafe_allow_html=True)

# Nota Metodológica Integrada
st.warning(
    "📌 **Nota Metodológica del Observatorio:** Los datos reflejan exclusivamente"
    " la **Red Asistencial Pública** (Hospitales, SAPU, SAR, etc.). El sector"
    " privado (clínicas) no reporta bajo este estándar abierto. La red pública"
    " cubre aproximadamente al 80% de la población nacional a través de Fonasa."
)
st.markdown("<br>", unsafe_allow_html=True)

# --- SECCIÓN 1: PANORAMA MACRO ---
st.markdown("## 1. La Presión Asistencial Global")
st.markdown(
    "<div class='story-card story-text'>Evolución del volumen total de"
    " atenciones de urgencia a nivel país, evidenciando la reactivación de la"
    " demanda asistencial tras los años críticos de la pandemia.</div>",
    unsafe_allow_html=True,
)

q_macro = (
    "SELECT anio, SUM(total_atenciones) as total FROM atenciones_urgencia GROUP"
    " BY anio ORDER BY anio;"
)
df_macro = ejecutar_consulta(q_macro)

col1, col2 = st.columns([1, 2], gap="large")
with col1:
  st.markdown("<br>", unsafe_allow_html=True)
  for _, r in df_macro.iterrows():
    st.metric(
        label=f"Volumen Total Año {int(r['anio'])}",
        value=f"{int(r['total']):,}".replace(",", "."),
    )
with col2:
  fig_macro = px.line(df_macro, x="anio", y="total", markers=True, text="total")
  fig_macro.update_traces(
      textposition="top center", line_color="#2563eb", line_width=4, marker_size=10
  )
  fig_macro.update_layout(
      title="Tendencia Interanual de Urgencias",
      template="plotly_white",
      yaxis_title="Atenciones Totales",
      xaxis_title="Año",
  )
  st.plotly_chart(fig_macro, width="stretch")

st.markdown(
    """
    <div class="insight-box">
        <b>💡 Lectura Estratégica para la Gestión:</b> El salto masivo observado entre 2021 y 2022 responde a la liberación de la 
        demanda contenida por las restricciones de movilidad. A partir de 2022, la carga se estabiliza en torno a los 24 millones de 
        atenciones anuales, fijando un nuevo "piso estructural" de presión para la red pública.
    </div>
""",
    unsafe_allow_html=True,
)

st.markdown("---")

# --- SECCIÓN 2: ESTACIONALIDAD ---
st.markdown("## 2. El Impacto Estacional y la Campaña de Invierno")
st.markdown(
    "<div class='story-card story-text'>Desglose semanal de la demanda médica"
    " durante el año 2023, aislando las patologías de origen respiratorio para"
    " medir el nivel de estrés operativo en los centros asistenciales.</div>",
    unsafe_allow_html=True,
)

q_semanal = """
SELECT semana, 
       SUM(CASE WHEN glosa_causa ILIKE '%respiratoria%' THEN total_atenciones ELSE 0 END) as "Causas_Respiratorias",
       SUM(CASE WHEN glosa_causa NOT ILIKE '%respiratoria%' THEN total_atenciones ELSE 0 END) as "Otras_Causas"
FROM atenciones_urgencia WHERE semana IS NOT NULL AND anio = 2023 GROUP BY semana ORDER BY semana;
"""
df_semanal = ejecutar_consulta(q_semanal)
df_semanal_melted = df_semanal.melt(
    id_vars="semana",
    value_vars=["Causas_Respiratorias", "Otras_Causas"],
    var_name="Tipo_Causa",
    value_name="Total_Atenciones",
)

fig_semana = px.area(
    df_semanal_melted,
    x="semana",
    y="Total_Atenciones",
    color="Tipo_Causa",
    title="Comportamiento Epidemiológico Semanal (Año 2023)",
    color_discrete_map={
        "Causas_Respiratorias": "#dc2626",
        "Otras_Causas": "#3b82f6",
    },
)
fig_semana.update_layout(
    xaxis_title="Semana Epidemiológica (1 - 52)",
    yaxis_title="Volumen de Atenciones",
    template="plotly_white",
)
st.plotly_chart(fig_semana, width="stretch")

st.markdown(
    """
    <div class="insight-box">
        <b>💡 Lectura Estratégica para la Gestión:</b> Mientras que los motivos basales (traumas, patologías digestivas) se mantienen 
        estables en azul, la ola roja muestra con precisión milimétrica el peak de virus respiratorios entre las semanas 22 y 30. 
        Este gráfico justifica la necesidad de anticipar presupuestos y contratos flexibles para personal clínico de refuerzo antes de junio.
    </div>
""",
    unsafe_allow_html=True,
)

st.markdown("---")

# --- SECCIÓN 3: CORRELACIÓN EDAD VS DIAGNÓSTICO ---
st.markdown("## 3. Demografía Sanitaria: ¿Quiénes Saturan las Urgencias?")
st.markdown(
    "<div class='story-card story-text'>Cruce de variables entre las"
    " principales causas médicas y los grupos etarios de los pacientes"
    " atendidos en el sistema público.</div>",
    unsafe_allow_html=True,
)

q_correlacion = """
SELECT glosa_causa, 
       SUM(menores_1 + de_1_a_4 + de_5_a_14) as "Pediátricos (0-14)",
       SUM(de_15_a_64) as "Adultos (15-64)",
       SUM(de_65_y_mas) as "Adultos Mayores (65+)"
FROM atenciones_urgencia
WHERE glosa_causa IS NOT NULL 
  AND glosa_causa NOT ILIKE '%otras%' 
  AND glosa_causa NOT ILIKE '%indiferenciado%'
GROUP BY glosa_causa
ORDER BY SUM(total_atenciones) DESC LIMIT 8;
"""
df_corr = ejecutar_consulta(q_correlacion)
df_melted = df_corr.melt(
    id_vars="glosa_causa", var_name="Grupo Etario", value_name="Atenciones"
)

fig_corr = px.bar(
    df_melted,
    x="Atenciones",
    y="glosa_causa",
    color="Grupo Etario",
    orientation="h",
    title="Distribución de Patologías por Segmento Etario",
    color_discrete_sequence=["#93c5fd", "#1e3a8a", "#dc2626"],
)
fig_corr.update_layout(
    barmode="stack",
    yaxis={"categoryorder": "total ascending"},
    template="plotly_white",
    yaxis_title="",
)
st.plotly_chart(fig_corr, width="stretch")

st.markdown(
    """
    <div class="insight-box">
        <b>💡 Lectura Estratégica para la Gestión:</b> Permite identificar claramente los nichos de riesgo por edad. Las patologías 
        respiratorias agudas concentran su peso en la franja infantil y en la tercera edad, exigiendo enfoques diferenciados de atención primaria 
        (vacunación temprana y campañas preventivas en colegios y hogares de larga estadía).
    </div>
""",
    unsafe_allow_html=True,
)

st.markdown("---")

# --- SECCIÓN 4: COMPOSICIÓN DE LA RED ---
st.markdown("## 4. Resolutividad Operativa de los Establecimientos")
q_tipo = """
SELECT tipo_establecimiento, SUM(total_atenciones) as total 
FROM atenciones_urgencia WHERE tipo_establecimiento IS NOT NULL GROUP BY tipo_establecimiento ORDER BY total DESC LIMIT 5;
"""
df_tipo = ejecutar_consulta(q_tipo)
fig_tipo = px.pie(
    df_tipo,
    names="tipo_establecimiento",
    values="total",
    hole=0.5,
    title="Participación porcentual por Tipología de Centro",
)
fig_tipo.update_traces(textposition="inside", textinfo="percent+label")
fig_tipo.update_layout(template="plotly_white", showlegend=False)
st.plotly_chart(fig_tipo, width="stretch")

st.markdown(
    """
    <div class="insight-box">
        <b>💡 Lectura Estratégica para la Gestión:</b> Los SAPU y SAR operan como los verdaderos escudos protectores del sistema hospitalario. 
        Fortalecer su capacidad de resolución evita que pacientes con patologías de baja complejidad saturen las urgencias de alta complejidad de los hospitales base.
    </div>
""",
    unsafe_allow_html=True,
)

st.markdown("---")

# --- SECCIÓN 5: EXPLORADOR DE DATOS INTERACTIVO ---
st.markdown("## 5. Módulo de Exploración y Extracción de Datos")
st.markdown(
    "<div class='story-card story-text'>Utiliza los siguientes filtros"
    " avanzados para realizar consultas cruzadas sobre millones de registros"
    " almacenados en PostgreSQL. Genera tablas a la medida y descargas directas"
    " en formato CSV.</div>",
    unsafe_allow_html=True,
)


@st.cache_data
def cargar_opciones_filtros():
  q_anios = "SELECT DISTINCT anio FROM atenciones_urgencia ORDER BY anio;"
  q_regiones = """
        SELECT DISTINCT nombre_region 
        FROM atenciones_urgencia 
        WHERE nombre_region IS NOT NULL AND nombre_region != '' 
        ORDER BY nombre_region;
    """
  df_r = ejecutar_consulta(q_regiones)
  if df_r.empty or len(df_r) == 0:
    q_regiones = """
            SELECT DISTINCT nombre_dependencia AS nombre_region 
            FROM atenciones_urgencia 
            WHERE nombre_dependencia IS NOT NULL AND nombre_dependencia != '' 
            ORDER BY nombre_dependencia;
        """
    df_r = ejecutar_consulta(q_regiones)

  q_tipos = "SELECT DISTINCT tipo_establecimiento FROM atenciones_urgencia WHERE tipo_establecimiento IS NOT NULL ORDER BY tipo_establecimiento;"

  df_a = ejecutar_consulta(q_anios)
  df_t = ejecutar_consulta(q_tipos)

  anios = df_a["anio"].tolist() if not df_a.empty else []
  regiones = df_r["nombre_region"].tolist() if not df_r.empty else []
  tipos = df_t["tipo_establecimiento"].tolist() if not df_t.empty else []

  return anios, regiones, tipos


anios_opt, regiones_opt, tipos_opt = cargar_opciones_filtros()

mapa_edades = {
    "Todas las edades (Total)": "total_atenciones",
    "Menores de 1 año": "menores_1",
    "1 a 4 años": "de_1_a_4",
    "5 a 14 años": "de_5_a_14",
    "15 a 64 años": "de_15_a_64",
    "65 y más años": "de_65_y_mas",
}

with st.container():
  st.markdown("### 🎛️ Panel de Filtros Dinámicos")
  col_f1, col_f2, col_f3, col_f4 = st.columns(4)
  with col_f1:
    f_anio = st.multiselect(
        "📅 Año", options=anios_opt, default=anios_opt[:1] if anios_opt else []
    )
  with col_f2:
    f_region = st.multiselect(
        "📍 Territorio / Red", options=regiones_opt, placeholder="Todos..."
    )
  with col_f3:
    f_tipo = st.multiselect(
        "🏥 Tipo Centro", options=tipos_opt, placeholder="Todos..."
    )
  with col_f4:
    f_edad = st.selectbox("👥 Grupo Etario", options=list(mapa_edades.keys()))

  st.markdown("<br>", unsafe_allow_html=True)

  if st.button(
      "🚀 Generar Reporte Personalizado", type="primary", width="stretch"
  ):
    with st.spinner("Procesando consulta masiva en la base de datos..."):

      condiciones = []
      if f_anio:
        anios_str = ",".join(map(str, f_anio))
        condiciones.append(f"anio IN ({anios_str})")

      if f_region:
        reg_str = ",".join([f"'{r}'" for r in f_region])
        condiciones.append(
            f"(nombre_region IN ({reg_str}) OR nombre_dependencia IN"
            f" ({reg_str}))"
        )

      if f_tipo:
        tipo_str = ",".join([f"'{t}'" for t in f_tipo])
        condiciones.append(f"tipo_establecimiento IN ({tipo_str})")

      where_clause = ""
      if condiciones:
        where_clause = "WHERE " + " AND ".join(condiciones)

      columna_sumar = mapa_edades[f_edad]

      query_tabla = f"""
            SELECT 
                anio AS "Año",
                COALESCE(nombre_region, nombre_dependencia) AS "Territorio / Red", 
                nombre_establecimiento AS "Establecimiento", 
                tipo_establecimiento AS "Tipo de Centro",
                glosa_causa AS "Causa Médica", 
                SUM({columna_sumar}) AS "Total Atenciones"
            FROM atenciones_urgencia
            {where_clause}
            GROUP BY anio, COALESCE(nombre_region, nombre_dependencia), nombre_establecimiento, tipo_establecimiento, glosa_causa
            HAVING SUM({columna_sumar}) > 0
            ORDER BY "Total Atenciones" DESC
            LIMIT 200;
            """

      df_resultado = ejecutar_consulta(query_tabla)

      if df_resultado.empty:
        st.warning(
            "No se registraron datos para esta combinación específica de"
            " filtros."
        )
      else:
        st.success(
            f"✅ Se han recuperado exitosamente {len(df_resultado)} registros"
            " agregados."
        )
        st.dataframe(df_resultado, width="stretch", hide_index=True)

        csv = df_resultado.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Descargar Dataset en Formato CSV",
            data=csv,
            file_name="reporte_minsal_estrategico.csv",
            mime="text/csv",
            width="stretch",
        )