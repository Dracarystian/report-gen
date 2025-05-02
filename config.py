import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuraciones generales
APP_NAME = "Report Creator"
VERSION = "1.0.0"

# Configuraciones de OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4"
OPENAI_TEMPERATURE = 0.4

# Configuraciones de Jira
JIRA_CONFIG = {
    "server": os.getenv("JIRA_SERVER"),
    "username": os.getenv("JIRA_USERNAME"),
    "token": os.getenv("JIRA_API_TOKEN"),
}

# Configuraciones de Figma 
#FIGMA_CONFIG = {
#    "access_token": os.getenv("FIGMA_ACCESS_TOKEN"),
#    "team_id": os.getenv("FIGMA_TEAM_ID"),
#}

# Configuraciones de Mautic (ejemplo)
#MAUTIC_CONFIG = {
#    "url": os.getenv("MAUTIC_URL"),
#    "username": os.getenv("MAUTIC_USERNAME"),
#    "password": os.getenv("MAUTIC_PASSWORD"),
#}

# Configuraciones de Mautic (ejemplo)


# Lista de integraciones disponibles
AVAILABLE_INTEGRATIONS = ["jira"] #figma, mautic, etc