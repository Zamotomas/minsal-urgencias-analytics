from fastapi import FastAPI
import psycopg2

app = FastAPI(title="API Minsal - Atenciones de Urgencia")

# Configuración segura de la base de datos usando Streamlit Secrets
DB_CONFIG = {
    "dbname": st.secrets["postgres"]["dbname"],
    "user": st.secrets["postgres"]["user"],
    "password": st.secrets["postgres"]["password"],
    "host": st.secrets["postgres"]["host"],
    "port": st.secrets["postgres"]["port"],
    "client_encoding": "utf8"
}

# Endpoint 1: Mensaje de bienvenida para saber que la API funciona
@app.get("/")
def leer_raiz():
    return {"mensaje": "¡Bienvenido a la API del MINSAL! El servidor está corriendo."}

# Endpoint 2: Obtener un resumen de atenciones por año
@app.get("/resumen_por_anio")
def resumen_por_anio():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Consulta SQL para agrupar por año
        query = """
        SELECT anio, SUM(total_atenciones) as total
        FROM atenciones_urgencia
        GROUP BY anio
        ORDER BY anio;
        """
        cursor.execute(query)
        resultados = cursor.fetchall()
        
        # Formatear la respuesta como una lista de diccionarios (JSON)
        datos = [{"anio": fila[0], "total_atenciones": fila[1]} for fila in resultados]
        
        cursor.close()
        conn.close()
        
        return {"data": datos}
    
    except Exception as e:
        return {"error": str(e)}