import os
import pandas as pd

DATA_DIR = "data"
MAX_SHEETS = 10

class ExcelIntegration:
    def __init__(self, config=None):
        self.config = config

    def verify_connection(self):
        """Verifica si la carpeta de datos existe."""
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        files = [f for f in os.listdir(DATA_DIR) if f.endswith(('.xlsx', '.xls'))]
        if files:
            return True, "Conexión exitosa a la carpeta de datos."
        else:
            return True, "Carpeta de datos lista, pero no se encontraron archivos Excel."

    def get_files(self):
        """Lista los archivos Excel en la carpeta 'data'."""
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        files = [f for f in os.listdir(DATA_DIR) if f.endswith(('.xlsx', '.xls'))]
        if files:
            return files, "Archivos Excel encontrados."
        else:
            return [], "No se encontraron archivos Excel en la carpeta 'data'."

    def fetch_data(self, file_name):
        """Lee hasta 10 hojas de un archivo Excel y retorna un dict con los datos."""
        file_path = os.path.join(DATA_DIR, file_name)
        if not os.path.exists(file_path):
            return None, "Archivo no encontrado."
        try:
            xls = pd.ExcelFile(file_path)
            sheets = {}
            for i, sheet_name in enumerate(xls.sheet_names):
                if i >= MAX_SHEETS:
                    break
                df = xls.parse(sheet_name)
                sheets[sheet_name] = df.head(100).to_dict(orient="records")
            return sheets, "Datos leídos correctamente."
        except Exception as e:
            return None, f"Error al leer el archivo: {e}"

    def generate_report_data(self, data):
        """Solicita contexto al usuario y prepara los datos para el informe."""
        print("\nPor favor, describe brevemente el contexto del archivo Excel y la información relevante que contiene:")
        context = input("Contexto: ")
        return {
            "contexto_usuario": context,
            "hojas": data
        }