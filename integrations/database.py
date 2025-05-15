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

    def fetch_database_overview(self):
        """
        Obtiene un resumen general de la base de datos: nombres de tablas y las primeras filas de cada una.
        """
        try:
            inspector = sqlalchemy.inspect(self.engine)
            tables = inspector.get_table_names()
            overview = {}
            for table in tables:
                try:
                    df = pd.read_sql(f"SELECT * FROM {table} LIMIT 5", self.engine)
                    df = df.astype(str)
                    overview[table] = {
                        "columns": list(df.columns),
                        "sample_rows": df.to_dict(orient="records")
                    }
                except Exception as e:
                    overview[table] = {
                        "columns": [],
                        "sample_rows": [],
                        "error": str(e)
                    }
            return overview, f"Resumen de {len(tables)} tablas obtenido correctamente."
        except Exception as e:
            return None, f"Error al obtener resumen de la base de datos: {e}"

    def generate_report_data(self, data):
        """Solicita contexto al usuario y prepara los datos para el informe."""
        print("\nDescribe brevemente el contexto del informe que deseas generar sobre la base de datos:")
        context = input("Contexto: ")
        return {
            "contexto_usuario": context,
            "resumen_bd": data
        }