import os
import pandas as pd
import sqlalchemy
from dotenv import load_dotenv

load_dotenv()

# Leer credenciales individuales y construir la URL de conexión
DB_NAME = os.getenv("DB_NAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_USER = os.getenv("DB_USER")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432") 

def build_postgres_url():
    """Construye la URL de conexión para PostgreSQL en RDS."""
    return f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

class DatabaseIntegration:
    def __init__(self):
        self.db_url = build_postgres_url()
        self.engine = None

    def verify_connection(self):
        """Verifica la conexión a la base de datos."""
        try:
            self.engine = sqlalchemy.create_engine(self.db_url)
            with self.engine.connect() as conn:
                conn.execute(sqlalchemy.text("SELECT 1"))
            return True, "Conexión exitosa a la base de datos."
        except Exception as e:
            return False, f"Error de conexión: {e}"

    def fetch_users_table(self, limit=1000):
        """Obtiene los datos de la tabla 'users'."""
        try:
            query = f"SELECT * FROM users LIMIT {limit}"
            df = pd.read_sql(query, self.engine)
            return df.to_dict(orient="records"), "Datos de la tabla 'users' obtenidos correctamente."
        except Exception as e:
            return None, f"Error al obtener datos: {e}"

    def generate_report_data(self, data):
        """Solicita contexto al usuario y prepara los datos para el informe."""
        print("\nDescribe brevemente el contexto del informe que deseas generar sobre la tabla 'users':")
        context = input("Contexto: ")
        return {
            "contexto_usuario": context,
            "tabla": "users",
            "datos": data
        }