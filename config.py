import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuraciones generales
APP_NAME = "Report Creator"
VERSION = "1.0.0"

# Configuraciones de OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4o"  # Versión con mayor capacidad de tokens
OPENAI_TEMPERATURE = 0.4

# Configuraciones de Jira
JIRA_CONFIG = {
    "server": os.getenv("JIRA_SERVER"),
    "username": os.getenv("JIRA_USERNAME"),
    "token": os.getenv("JIRA_API_TOKEN"),
}

# Configuración de Excel
EXCEL_CONFIG = {
    "data_dir": "data"  
}

# Lista de integraciones disponibles
AVAILABLE_INTEGRATIONS = ["jira", "excel"]