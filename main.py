import os
import config
from datetime import datetime
from integrations.jira import JiraIntegration
from integrations.excel import ExcelIntegration
from integrations.database import DatabaseIntegration  
from services.openai import generate_report
from services.exports import convert_report

def main():
    print(f"🚀 Bienvenido a {config.APP_NAME} v{config.VERSION}")

    # Mostrar integraciones disponibles con nombres amigables
    print("\n📊 Integraciones disponibles:")
    for i, integration in enumerate(config.AVAILABLE_INTEGRATIONS, 1):
        display_name = config.INTEGRATION_DISPLAY_NAMES.get(integration, integration.capitalize())
        print(f"{i}. {display_name}")

    # Selección de integración
    try:
        choice = int(input("\nSeleccione una integración (número): ")) - 1
        selected = config.AVAILABLE_INTEGRATIONS[choice]
    except (ValueError, IndexError):
        print("❌ Selección inválida. Usando Jira por defecto.")
        selected = "jira"

    print(f"\n🔄 Inicializando integración con {selected.capitalize()}...")

    # Diccionario de casos de uso (switch)
    use_cases = {
        "jira": handle_jira_integration,
        "excel": handle_excel_integration,
        "database": handle_database_integration
    }

    handler = use_cases.get(selected)
    if handler:
        handler()
    else:
        print(f"❌ Integración {selected} no implementada.")

def handle_jira_integration():
    """Maneja el flujo de trabajo para integración con Jira."""
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
    
    # Obtener datos para el informe
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
    report = generate_report(
        report_data, 
        f"Jira - {selected_project.name}", 
        report_focus=report_config["focus"]
    )
    
    # Seleccionar formato de salida
    filename_base = f"jira_{selected_project.key}"
    output_file = select_and_export_format(report, filename_base)
    
    # Mostrar vista previa
    print("\n📄 Vista previa del informe:\n")
    print(report[:500] + "...\n")
    print(f"Informe completo disponible en: {output_file}")

def handle_excel_integration():
    """Maneja el flujo de trabajo para integración con Excel local."""
    integration = ExcelIntegration(config.EXCEL_CONFIG)
    success, message = integration.verify_connection()
    
    if not success:
        print(f"❌ {message}")
        return
    
    print(f"✅ {message}")
    
    # Obtener archivos disponibles
    files, message = integration.get_files()
    print(f"\n📁 {message}")
    
    if not files:
        print("❌ No se encontraron archivos Excel.")
        return
    
    # Listar archivos
    for i, file in enumerate(files, 1):
        print(f"{i}. {file}")
    
    # Seleccionar archivo
    try:
        file_idx = int(input("\nSeleccione un archivo (número): ")) - 1
        selected_file = files[file_idx]
        print(f"\n🔍 Leyendo archivo '{selected_file}'...")
    except (ValueError, IndexError):
        print("❌ Selección inválida.")
        return
    
    # Leer archivo
    data, message = integration.fetch_data(file_name=selected_file)
    print(f"✅ {message}")
    
    if data is None:
        print("❌ No se pudieron leer los datos del archivo.")
        return
    
    # Si es un archivo con múltiples hojas, permitir elegir
    if isinstance(data, dict):
        print("\n📊 Hojas disponibles:")
        for i, sheet in enumerate(data.keys(), 1):
            print(f"{i}. {sheet}")
        
        try:
            sheet_idx = int(input("\nSeleccione una hoja (número) o 0 para todas: ")) - 1
            if sheet_idx >= 0:
                selected_sheet = list(data.keys())[sheet_idx]
                data = data[selected_sheet]
                print(f"✅ Seleccionada hoja '{selected_sheet}'")
            # Si es 0 o negativo, se usan todas las hojas
        except (ValueError, IndexError):
            print("❌ Selección inválida, usando todas las hojas.")
    
    # Generar datos para el informe
    report_data = integration.generate_report_data(data)
    
    # Generar informe con AI
    print("\n🧠 Generando informe con OpenAI...")
    report = generate_report(
        report_data, 
        f"Excel - {os.path.splitext(selected_file)[0]}", 
        report_focus="excel_data"
    )
    
    # Seleccionar formato de salida
    filename_base = f"excel_{os.path.splitext(selected_file)[0]}"
    output_file = select_and_export_format(report, filename_base)
    
    # Mostrar vista previa
    print("\n📄 Vista previa del informe:\n")
    print(report[:500] + "...\n")
    print(f"Informe completo disponible en: {output_file}")

def handle_database_integration():
    """Maneja el flujo de trabajo para integración con base de datos."""
    integration = DatabaseIntegration()
    success, message = integration.verify_connection()
    if not success:
        print(f"❌ {message}")
        return

    print(f"✅ {message}")

    # Obtener datos de la tabla users
    data, msg = integration.fetch_database_overview()
    print(f"\n📁 {msg}")

    if not data:
        print("❌ No se encontraron datos en la tabla 'users'.")
        return

    # Generar datos para el informe
    report_data = integration.generate_report_data(data)

    # Generar informe con AI
    print("\n🧠 Generando informe con OpenAI...")
    report = generate_report(
        report_data,
        "Base de datos - users",
        report_focus="general"
    )

    # Seleccionar formato de salida
    filename_base = "db_users"
    output_file = select_and_export_format(report, filename_base)

    # Mostrar vista previa
    print("\n📄 Vista previa del informe:\n")
    print(report[:500] + "...\n")
    print(f"Informe completo disponible en: {output_file}")

def select_and_export_format(report, filename_base):
    """Permite seleccionar el formato de salida y exporta el informe."""
    # Formato de salida
    format_options = {
        1: {"name": "Markdown (.md)", "code": "md"},
        2: {"name": "PDF (.pdf)", "code": "pdf"},
        3: {"name": "Excel (.xlsx)", "code": "excel"},
        4: {"name": "LaTeX (.tex)", "code": "latex"}
    }
    
    # Mostrar opciones
    print("\n📂 Seleccione el formato de salida:")
    for k, v in format_options.items():
        print(f"{k}. {v['name']}")
    
    # Obtener selección
    selected_format = "md"  # Valor predeterminado
    try:
        format_choice = int(input("\nSeleccione formato (número): "))
        format_config = format_options.get(format_choice)
        if format_config:
            selected_format = format_config["code"]
        else:
            print("❌ Formato no válido, usando Markdown")
    except (ValueError, KeyError):
        print("❌ Formato no válido, usando Markdown")
    
    # Convertir y guardar
    output_file = convert_report(report, selected_format, filename_base)
    print(f"\n✅ Informe guardado como: {output_file}")
    
    return output_file

if __name__ == "__main__":
    main()
