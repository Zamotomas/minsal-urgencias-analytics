import os
import duckdb
import psycopg2

# 1. Configuración de conexión a PostgreSQL
# Configuración segura de la base de datos usando Streamlit Secrets
DB_CONFIG = {
    "dbname": st.secrets["postgres"]["dbname"],
    "user": st.secrets["postgres"]["user"],
    "password": st.secrets["postgres"]["password"],
    "host": st.secrets["postgres"]["host"],
    "port": st.secrets["postgres"]["port"],
    "client_encoding": "utf8"
}

# 2. Ruta exacta hacia la carpeta con tus archivos CSV
CARPETA_CSV = "./test/atencionesUrgencia/*.csv"

def preparar_base_de_datos():
    print("🛠️ Preparando la base de datos (recreando tablas particionadas)...")
    # Conectamos con autocommit para poder ejecutar comandos de DROP/CREATE
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True 
    cursor = conn.cursor()
    
    sql_setup = """
    DROP TABLE IF EXISTS atenciones_urgencia CASCADE;

    CREATE TABLE atenciones_urgencia (
        id BIGINT GENERATED ALWAYS AS IDENTITY,
        fecha DATE NOT NULL,
        anio INT NOT NULL,
        semana INT,
        id_establecimiento VARCHAR(50),
        nombre_establecimiento VARCHAR(200),
        tipo_establecimiento VARCHAR(100),
        tipo_atencion VARCHAR(100),
        tipo_campana VARCHAR(100),
        codigo_region INT,
        nombre_region VARCHAR(100),
        codigo_dependencia INT,
        nombre_dependencia VARCHAR(150),
        codigo_comuna INT,
        nombre_comuna VARCHAR(100),
        id_causa INT,
        glosa_causa VARCHAR(200),
        total_atenciones INT,
        menores_1 INT,
        de_1_a_4 INT,
        de_5_a_14 INT,
        de_15_a_64 INT,
        de_65_y_mas INT,
        PRIMARY KEY (id, anio)
    ) PARTITION BY RANGE (anio);

    -- Creación de particiones garantizadas
    CREATE TABLE atenciones_urgencia_2020 PARTITION OF atenciones_urgencia FOR VALUES FROM (2020) TO (2021);
    CREATE TABLE atenciones_urgencia_2021 PARTITION OF atenciones_urgencia FOR VALUES FROM (2021) TO (2022);
    CREATE TABLE atenciones_urgencia_2022 PARTITION OF atenciones_urgencia FOR VALUES FROM (2022) TO (2023);
    CREATE TABLE atenciones_urgencia_2023 PARTITION OF atenciones_urgencia FOR VALUES FROM (2023) TO (2024);
    CREATE TABLE atenciones_urgencia_2024 PARTITION OF atenciones_urgencia FOR VALUES FROM (2024) TO (2025);
    CREATE TABLE atenciones_urgencia_2025 PARTITION OF atenciones_urgencia FOR VALUES FROM (2025) TO (2026);
    CREATE TABLE atenciones_urgencia_default PARTITION OF atenciones_urgencia DEFAULT;

    -- Índices
    CREATE INDEX idx_urg_fecha ON atenciones_urgencia (fecha);
    CREATE INDEX idx_urg_causa ON atenciones_urgencia (id_causa);
    """
    
    cursor.execute(sql_setup)
    cursor.close()
    conn.close()
    print("✅ Base de datos estructurada y lista.")

def ejecutar_etl():
    # Primero garantizamos que la estructura exista
    preparar_base_de_datos()
    
    print("🚀 Iniciando procesamiento de los 4 archivos CSV del MINSAL...")

    # Conectar a DuckDB en memoria
    con = duckdb.connect(database=":memory:")

    # 3. Transformación con DuckDB adaptada a las 15 columnas
    query_transformacion = f"""
    SELECT 
        TRY_CAST(fecha::VARCHAR AS DATE) AS fecha,
        YEAR(TRY_CAST(fecha::VARCHAR AS DATE)) AS anio,
        TRY_CAST(semana AS INT) AS semana,
        
        IdEstablecimiento AS id_establecimiento,
        NEstablecimiento AS nombre_establecimiento,
        GLOSATIPOESTABLECIMIENTO AS tipo_establecimiento,
        GLOSATIPOATENCION AS tipo_atencion,
        GlosaTipoCampana AS tipo_campana,
        
        NULL::INT AS codigo_region,
        NULL::VARCHAR AS nombre_region,
        NULL::INT AS codigo_dependencia,
        NULL::VARCHAR AS nombre_dependencia,
        NULL::INT AS codigo_comuna,
        NULL::VARCHAR AS nombre_comuna,
        
        TRY_CAST(IdCausa AS INT) AS id_causa,
        TRIM(GlosaCausa) AS glosa_causa,
        TRY_CAST(Total AS INT) AS total_atenciones,
        TRY_CAST(Menores_1 AS INT) AS menores_1,
        TRY_CAST(De_1_a_4 AS INT) AS de_1_a_4,
        TRY_CAST(De_5_a_14 AS INT) AS de_5_a_14,
        TRY_CAST(De_15_a_64 AS INT) AS de_15_a_64,
        TRY_CAST(De_65_y_mas AS INT) AS de_65_y_mas
    FROM read_csv_auto('{CARPETA_CSV}', header=True, ignore_errors=True, delim=';')
    WHERE fecha IS NOT NULL
    """

    print("📊 Mapeando y transformando datos en memoria...")

    # 4. Generar archivo CSV limpio temporal
    csv_temp = "temp_minsal_procesado.csv"
    con.execute(
        f"COPY ({query_transformacion}) TO '{csv_temp}' (HEADER, DELIMITER ',')"
    )
    print("✅ Transformación en DuckDB completada.")

    # 5. Inserción masiva en PostgreSQL
    print("🐘 Cargando datos a PostgreSQL (método COPY)...")
    conn_pg = psycopg2.connect(**DB_CONFIG)
    cursor = conn_pg.cursor()

    with open(csv_temp, "r", encoding="utf-8") as f:
        next(f)  # Saltar encabezado
        cursor.copy_expert(
            """
            COPY atenciones_urgencia(
                fecha, anio, semana,
                id_establecimiento, nombre_establecimiento, tipo_establecimiento, tipo_atencion, tipo_campana,
                codigo_region, nombre_region, codigo_dependencia, nombre_dependencia, codigo_comuna, nombre_comuna,
                id_causa, glosa_causa, total_atenciones,
                menores_1, de_1_a_4, de_5_a_14, de_15_a_64, de_65_y_mas
            ) FROM STDIN WITH CSV DELIMITER ','
            """,
            f,
        )

    conn_pg.commit()
    cursor.close()
    conn_pg.close()

    # Eliminar archivo temporal
    if os.path.exists(csv_temp):
        os.remove(csv_temp)

    print("🎉 ¡Proceso finalizado! Los 4 archivos se cargaron correctamente a PostgreSQL.")

if __name__ == "__main__":
    ejecutar_etl()