import json
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE

# Cliente de OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

def generate_report(data, report_type, format_type="markdown", report_focus="general"):
    """Genera un informe usando OpenAI basado en los datos proporcionados."""
    
    # Instrucciones base
    system_base = f"""Eres un analista experto en generación de informes profesionales de {report_type}.
    Tu tarea es crear un informe detallado, claro y ejecutivo basado en los datos proporcionados.
    """
    
    # Instrucciones específicas según el enfoque
    focus_instructions = {
        "general": """Enfócate en dar una visión general de todos los datos, mostrando tendencias y patrones.""",
        "sprint_activo": """Este es un análisis del sprint activo. Enfócate en el progreso, distribución de incidencias y posibles riesgos.""",
        "sprints_finalizados": """Analiza los sprints finalizados para identificar tendencias, eficiencia y lecciones aprendidas.""",
        "etiquetas": """Realiza un análisis detallado de las etiquetas, su relación con otros elementos y recomendaciones.""",
        "jerarquico": """Analiza la estructura jerárquica, identificando épicas principales, su progreso y dependencias.""",
        "excel_data": """Analiza los datos de Excel proporcionados, identificando tendencias, valores atípicos y oportunidades de mejora."""
    }
    
    # Combinar instrucciones
    system_message = system_base + focus_instructions.get(report_focus, focus_instructions["general"])
    
    # Añadir estructura estándar del informe
    system_message += """
    El informe debe incluir:
    1. Un título apropiado
    2. Un resumen ejecutivo
    3. Análisis de los datos principales según el enfoque solicitado
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