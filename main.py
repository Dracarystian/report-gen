import os
import json
from openai import OpenAI
from datetime import datetime
from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE
from integrations.jira import JiraIntegration
import config

# Configurar OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

def generate_report_with_ai(data, report_type, format_type="markdown", report_focus="general"):
    """Genera un informe usando OpenAI basado en los datos proporcionados."""
    
    system_message = f"""Eres un analista experto en generación de informes profesionales de {report_type}.
    Tu tarea es crear un informe detallado, claro y ejecutivo basado en los datos proporcionados.
    El informe debe incluir:
    1. Un título apropiado
    2. Un resumen ejecutivo
    3. Análisis de los datos principales
    4. Conclusiones y recomendaciones
    5. Formato profesional y estructurado
    """
    
    user_message = f"""Por favor genera un informe de {report_type} con los siguientes datos:
    
    {json.dumps(data, indent=2, ensure_ascii=False)}
    
    El informe debe ser en español y en formato {format_type}.
    """
    
    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=OPENAI_TEMPERATURE
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Error al generar informe: {str(e)}"

def save_report(content, report_type, format="md"):
    """Guarda el informe generado en un archivo."""
    # Crear directorio de informes si no existe
    reports_dir = "reports"
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
    
    # Crear nombre de archivo con fecha y hora
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{reports_dir}/{report_type}_report_{timestamp}.{format}"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    
    return filename

def main():
    print(f"🚀 Bienvenido a {config.APP_NAME} v{config.VERSION}")
    
    # Mostrar integraciones disponibles
    print("\n📊 Integraciones disponibles:")
    for i, integration in enumerate(config.AVAILABLE_INTEGRATIONS, 1):
        print(f"{i}. {integration.capitalize()}")
    
    # Selección de integración
    try:
        choice = int(input("\nSeleccione una integración (número): ")) - 1
        selected = config.AVAILABLE_INTEGRATIONS[choice]
    except (ValueError, IndexError):
        print("❌ Selección inválida. Usando Jira por defecto.")
        selected = "jira"
    
    print(f"\n🔄 Inicializando integración con {selected.capitalize()}...")
    
    # Inicializar la integración seleccionada
    if selected == "jira":
        integration = JiraIntegration(config.JIRA_CONFIG)
        success, message = integration.verify_connection()
        
        if not success:
            print(f"❌ {message}")
            return
        
        print(f"✅ {message}")
        
        # Obtener proyectos
        projects, message = integration.get_projects()
        print(f"\n📁 {message}")
        
        if not projects:
            print("❌ No se encontraron proyectos. Verifique sus permisos.")
            return
        
        # Listar proyectos
        for i, project in enumerate(projects, 1):
            print(f"{i}. {project.name} (Clave: {project.key})")
        
        # Seleccionar proyecto
        try:
            project_idx = int(input("\nSeleccione un proyecto (número): ")) - 1
            selected_project = projects[project_idx]
            print(f"\n🔍 Consultando datos de '{selected_project.name}'...")
        except (ValueError, IndexError):
            print("❌ Selección inválida.")
            return
        
        # Opciones de informe
        report_options = {
            1: {"name": "Incidencias actuales (todas)", "focus": "general", "params": {}},
            2: {"name": "Sprint activo", "focus": "sprint_activo", "params": {"sprint_state": "active"}},
            3: {"name": "Sprints finalizados", "focus": "sprints_finalizados", "params": {"sprint_state": "closed"}},
            4: {"name": "Análisis por etiquetas", "focus": "etiquetas", "params": {"include_labels": True}},
            5: {"name": "Análisis jerárquico", "focus": "jerarquico", "params": {"include_epics": True}}
        }
        
        # Mostrar opciones
        print("\n🔄 Seleccione el tipo de informe:")
        for k, v in report_options.items():
            print(f"{k}. {v['name']}")
        
        # Obtener selección con valor predeterminado
        try:
            report_choice = int(input("\nSeleccione tipo de informe (número): "))
            report_config = report_options.get(report_choice, report_options[1])
        except (ValueError, IndexError, KeyError):
            print("❌ Opción no válida, usando todas las incidencias")
            report_config = report_options[1]
        
        print(f"\n🔍 Generando informe: {report_config['name']}...")
        
        # Obtener datos con los parámetros configurados
        params = {"project_key": selected_project.key, "max_results": 100}
        params.update(report_config["params"])
        
        issues, count = integration.fetch_data(**params)
        
        if isinstance(count, str):  # Es un mensaje de error
            print(f"❌ {count}")
            return
            
        print(f"✅ Se encontraron {count} incidencias")
        
        # Generar datos para el informe
        report_data = integration.generate_report_data(issues)
        
        # Generar informe con AI
        print("\n🧠 Generando informe con OpenAI...")
        report = generate_report_with_ai(
            report_data, 
            f"Jira - {selected_project.name}", 
            report_focus=report_config["focus"]
        )
        
        # Guardar y mostrar informe
        filename = save_report(report, f"jira_{selected_project.key}")
        print(f"\n✅ Informe guardado en: {filename}")
        
        print("\n📄 Vista previa del informe:\n")
        print(report[:500] + "...\n")
        print("(Consulta el archivo para ver el informe completo)")

if __name__ == "__main__":
    main()
