import os
import requests
from dotenv import load_dotenv
import base64
from jira import JIRA
from integrations.base import BaseIntegration

# Cargar variables de entorno
load_dotenv()

JIRA_SERVER = os.getenv("JIRA_SERVER")
JIRA_USERNAME = os.getenv("JIRA_USERNAME")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

class JiraIntegration(BaseIntegration):
    def __init__(self, config):
        super().__init__(config)
        self.server = config["server"]
        self.username = config["username"]
        self.token = config["token"]
        self.client = None
    
    def verify_connection(self):
        """Verifica la conexión con Jira."""
        try:
            self.client = JIRA(server=self.server, basic_auth=(self.username, self.token))
            user = self.client.myself()
            return True, f"Conexión exitosa como: {user.get('displayName')}"
        except Exception as e:
            return False, f"Error de conexión: {str(e)}"
    
    def get_projects(self):
        """Obtiene la lista de proyectos disponibles."""
        if not self.client:
            _, message = self.verify_connection()
            if not self.client:
                return [], message
                
        try:
            projects = self.client.projects()
            return projects, f"Se encontraron {len(projects)} proyectos"
        except Exception as e:
            return [], f"Error al obtener proyectos: {str(e)}"
    
    def fetch_data(self, project_key=None, jql=None, max_results=50, 
                   sprint_id=None, sprint_state=None, include_epics=True, 
                   include_labels=True):
        """Obtiene incidencias de Jira según criterios especificados."""
        if not self.client:
            self.verify_connection()
        
        # Usar diccionario para mapear estados de sprint a JQL
        sprint_state_mapping = {
            'active': "sprint in openSprints()",
            'closed': "sprint in closedSprints()",
            'future': "sprint in futureSprints()"
        }
        
        # Construir JQL con componentes
        jql_components = []
        
        if project_key:
            jql_components.append(f"project = {project_key}")
            
        if sprint_id:
            jql_components.append(f"sprint = {sprint_id}")
        elif sprint_state in sprint_state_mapping:
            jql_components.append(sprint_state_mapping[sprint_state])
        
        # Usar el JQL personalizado o construir uno con los componentes
        jql_query = jql if jql else " AND ".join(jql_components)
        
        try:
            print(f"Ejecutando consulta JQL: {jql_query}")
            issues = self.client.search_issues(jql_query, maxResults=max_results)
            return issues, len(issues)
        except Exception as e:
            return [], f"Error al buscar incidencias: {str(e)}"
    
    def generate_report_data(self, issues):
        """Prepara los datos de las incidencias para el informe."""
        if not issues:
            return {"error": "No hay incidencias para generar informe"}
        
        # Función auxiliar para extraer datos seguros de un campo
        def safe_get(obj, attr, default=''):
            try:
                parts = attr.split('.')
                for part in parts:
                    if not obj:
                        return default
                    obj = getattr(obj, part, None)
                return obj if obj is not None else default
            except:
                return default
        
        # Función para extraer sprint info
        def extract_sprint(issue):
            try:
                sprints = getattr(issue.fields, 'customfield_10020', None)
                if isinstance(sprints, list) and sprints:
                    sprint_info = sprints[0]
                    if isinstance(sprint_info, str) and "name=" in sprint_info:
                        return sprint_info.split("name=")[1].split(",")[0]
                    return str(sprint_info)
                return "No asignado"
            except:
                return "No asignado"
        
        # Extraer datos de las incidencias
        issues_data = []
        label_counts = {}
        type_counts = {}
        status_counts = {}
        assignee_counts = {}
        epic_issues = {}
        
        # Mapeo de campos clave
        field_mapping = {
            "key": lambda i: i.key,
            "summary": lambda i: safe_get(i.fields, 'summary'),
            "status": lambda i: safe_get(i.fields, 'status.name'),
            "assignee": lambda i: safe_get(i.fields, 'assignee.displayName', 'Sin asignar'),
            "reporter": lambda i: safe_get(i.fields, 'reporter.displayName', 'Desconocido'),
            "created": lambda i: safe_get(i.fields, 'created'),
            "priority": lambda i: safe_get(i.fields, 'priority.name', 'No definida'),
            "description": lambda i: safe_get(i.fields, 'description', 'Sin descripción'),
            "type": lambda i: safe_get(i.fields, 'issuetype.name', 'Tarea'),
            "sprint": extract_sprint,
            "labels": lambda i: getattr(i.fields, 'labels', [])
        }
        
        # Procesar cada incidencia
        for issue in issues:
            # Extraer datos mediante mapeo
            issue_data = {field: getter(issue) for field, getter in field_mapping.items()}
            
            # Actualizar contadores
            status = issue_data["status"]
            assignee = issue_data["assignee"]
            issue_type = issue_data["type"]
            
            status_counts[status] = status_counts.get(status, 0) + 1
            assignee_counts[assignee] = assignee_counts.get(assignee, 0) + 1
            type_counts[issue_type] = type_counts.get(issue_type, 0) + 1
            
            # Contar etiquetas
            for label in issue_data["labels"]:
                label_counts[label] = label_counts.get(label, 0) + 1
            
            # Capturar relaciones jerárquicas (épicas)
            epic_key = safe_get(issue.fields, 'customfield_10014')
            if epic_key:
                issue_data["epic"] = epic_key
                epic_issues.setdefault(epic_key, []).append(issue.key)
                
            issues_data.append(issue_data)
        
        # Construir estructura de informe
        return {
            "total_issues": len(issues_data),
            "issues": issues_data,
            "statistics": {
                "by_status": status_counts,
                "by_assignee": assignee_counts,
                "by_type": type_counts,
                "by_label": label_counts,
                "by_epic": {epic: len(issues) for epic, issues in epic_issues.items()}
            },
            "hierarchy": epic_issues
        }

def listar_proyectos_detalle():
    """Lista todos los proyectos disponibles con detalles adicionales."""
    url = f"{JIRA_SERVER}/rest/api/2/project"
    headers = {
        "Authorization": f"Basic {requests.auth._basic_auth_str(JIRA_USERNAME, JIRA_API_TOKEN)}",
        "Content-Type": "application/json"
    }
    
    print(f"Conectando a {JIRA_SERVER} con usuario {JIRA_USERNAME}")
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        projects = response.json()
        
        print(f"\n✅ Se encontraron {len(projects)} proyectos disponibles:")
        for project in projects:
            print(f"\n• Nombre: {project['name']}")
            print(f"  Clave: {project['key']}")
            print(f"  ID: {project['id']}")
            print(f"  Tipo: {project.get('projectTypeKey', 'No especificado')}")
        
        return projects
    except Exception as e:
        print(f"❌ Error al listar proyectos: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Contenido de la respuesta: {e.response.text}")
        return []

def verificar_conexion_jira():
    """Realiza una verificación simple de conexión a Jira."""
    url = f"{JIRA_SERVER}/rest/api/2/myself"
    
    # Crear manualmente el header de autenticación
    auth_str = f"{JIRA_USERNAME}:{JIRA_API_TOKEN}"
    encoded_auth = base64.b64encode(auth_str.encode()).decode()
    
    headers = {
        "Authorization": f"Basic {encoded_auth}",
        "Content-Type": "application/json"
    }
    
    print(f"Intentando conectar a {JIRA_SERVER} con usuario {JIRA_USERNAME}...")
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print("✅ Conexión a Jira exitosa!")
            print(f"   Usuario autenticado: {response.json().get('displayName', 'Desconocido')}")
            return True
        else:
            print(f"❌ Error en la conexión. Código: {response.status_code}")
            print(f"   Mensaje: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error al conectar con Jira: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Verificando conexión básica a Jira...")
    verificar_conexion_jira()
    print("🔍 Comprobando conexión a Jira y listando proyectos con detalles...")
    listar_proyectos_detalle()